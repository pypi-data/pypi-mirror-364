#include "presign.h"


std::string hexEncode(const unsigned char *data, size_t len) {
    std::stringstream ss;
    ss << std::hex << std::setfill('0');
    for (size_t i = 0; i < len; ++i) {
        ss << std::setw(2) << static_cast<unsigned int>(data[i]);
    }
    return ss.str();
}

std::string uriEncode(const std::string &str, bool encodeSlash = true) {
    std::string result;
    char c;
    int i;
    for (auto &ch: str) {
        c = ch;
        if (std::isalnum(c) || c == '-' || c == '_' || c == '~' || c == '.' || (c == '/' && !encodeSlash)) {
            result += c;
        } else if (c == ' ') {
            result += "%20";
        } else {
            result += '%';
            i = static_cast<unsigned char>(c);
            result += "0123456789ABCDEF"[i / 16];
            result += "0123456789ABCDEF"[i % 16];
        }
    }
    return result;
}

const unsigned char *generateSignatureKey(
        const std::string &secretKey,
        const std::string &dateStamp,
        const std::string &region,
        const std::string &service,
        unsigned char *key,
        unsigned int *keyLength
) {
    const std::string kSecret = "AWS4" + secretKey;

//    std::cout << "kSecret" << std::endl;
//    std::cout << kSecret << std::endl;
    auto *kDate = (unsigned char *) malloc(32);
    auto kDateLength = (unsigned int *) malloc(1);
    HMAC(EVP_sha256(),
         kSecret.c_str(),
         int(kSecret.length()),
         reinterpret_cast<const unsigned char *>(dateStamp.c_str()),
         dateStamp.length(),
         kDate,
         kDateLength);

//    std::cout << "kDate" << ' ' << *kDateLength << std::endl;
//    std::cout << hexEncode(kDate, *kDateLength) << std::endl;
//    std::cout << kDate << std::endl;

    auto kRegion = (unsigned char *) malloc(32);
    auto kRegionLength = (unsigned int *) malloc(1);

    HMAC(EVP_sha256(),
         kDate,
         int(*kDateLength),
         reinterpret_cast<const unsigned char *>(region.c_str()),
         region.length(),
         kRegion,
         kRegionLength);

//    std::cout << "kRegion" << ' ' << *kRegionLength << std::endl;
//    std::cout << hexEncode(kRegion, *kRegionLength) << std::endl;
//    std::cout << kRegion << std::endl;

    auto *kService = (unsigned char *) malloc(32);
    auto *kServiceLength = (unsigned int *) malloc(1);

    HMAC(EVP_sha256(),
         kRegion,
         int(*kRegionLength),
         reinterpret_cast<const unsigned char *>(service.c_str()),
         service.length(),
         kService,
         kServiceLength);

//    std::cout << "kService" << ' ' << *kServiceLength << std::endl;
//    std::cout << hexEncode(kService, int(*kServiceLength)) << std::endl;
//    std::cout << kService << std::endl;


//    auto kSigning = (unsigned char *) malloc(32);
//    auto kSigningLength = (unsigned int *) malloc(1);

    HMAC(EVP_sha256(),
         kService,
         int(*kServiceLength),
         reinterpret_cast<const unsigned char *>("aws4_request"),
         std::strlen("aws4_request"),
         key,
         keyLength);

//    std::cout << "kSigning" << std::endl;
//    std::cout << hexEncode(key, *keyLength) << std::endl;
//    std::cout << key << std::endl;

    return nullptr;
}

std::string generateSignature(const unsigned char *signingKey, const unsigned int *signingKeyLegth,
                              const std::string &stringToSign) {

    auto digest = (unsigned char *) malloc(32);
    auto digestLength = (unsigned int *) malloc(1);

//    std::cout << "signingKey HEX " << hexEncode(signingKey, *signingKeyLegth) << std::endl;
//    std::cout << "sting to sign" << std::endl << stringToSign << std::endl;

    HMAC(EVP_sha256(), signingKey, int(*signingKeyLegth),
         reinterpret_cast<const unsigned char *>(stringToSign.c_str()), stringToSign.length(),
         digest, digestLength);
    std::string signature = hexEncode(digest, SHA256_DIGEST_LENGTH);
//    std::string signature = hexEncode(digest, SHA256_DIGEST_LENGTH);
    return signature;
}

std::string generatePresignedURL(const std::string &accessKey, const std::string &secretKey, const std::string &region,
                                 const std::string &bucket, const std::string &key, int expiresInSeconds, const std::string &endpoint) {
    std::time_t now = std::time(nullptr);
    std::tm tmTime;
    gmtime_r(&now, &tmTime);

    char dateStamp[9];
    strftime(dateStamp, sizeof(dateStamp), "%Y%m%d", &tmTime);

    char amzDate[17];
    strftime(amzDate, sizeof(amzDate), "%Y%m%dT%H%M%SZ", &tmTime);

    std::string algorithm = "AWS4-HMAC-SHA256";
//    std::string region = "us-east-1";
    std::string service = "s3";
    std::ostringstream credentialScope;

    credentialScope << dateStamp << "/" << region << "/" << service << "/aws4_request";

    std::string encodedKey = uriEncode(key, false);

    std::ostringstream queryParams;

    queryParams << "X-Amz-Algorithm=" << algorithm;
    queryParams << "&X-Amz-Credential="
                 << uriEncode(accessKey + "/" + dateStamp + "/" + region + "/" + service + "/aws4_request");
    queryParams << "&X-Amz-Date=" << amzDate;
    queryParams << "&X-Amz-Expires=" << expiresInSeconds;
    queryParams << "&X-Amz-SignedHeaders=host";

    std::string canonicalRequest =
            "GET\n/" + encodedKey + "\n" + queryParams.str() + "\nhost:" + bucket + "." + endpoint + "\n\nhost\nUNSIGNED-PAYLOAD";

//    std::cout << "Canonical" << std::endl << canonicalRequest << std::endl;
    auto *canonicalRequestHash = (unsigned char*)malloc(32);
    SHA256(reinterpret_cast<const unsigned char *>(canonicalRequest.c_str()),
           canonicalRequest.length(),
           canonicalRequestHash);

    std::string canonicalRequestHashHex = hexEncode(canonicalRequestHash, 32);

//    std::cout << "calculated canonical hash: " << canonicalRequestHashHex << std::endl;

    std::string stringToSign = algorithm + "\n" + amzDate + "\n" + credentialScope.str() + "\n" +
                               canonicalRequestHashHex;

//    std::cout << "String to Sign" << std::endl << stringToSign << std::endl;

    auto signingKey = (unsigned char *) malloc(32);
    auto signingKeyLength = (unsigned int *) malloc(1);

    generateSignatureKey(secretKey, dateStamp, region, service, signingKey, signingKeyLength);
    std::string signature = generateSignature(signingKey, signingKeyLength, stringToSign);

    std::ostringstream presignedURL;
    presignedURL << "https://" << bucket << "." << endpoint << "/" << encodedKey;
    presignedURL << "?X-Amz-Algorithm=" << algorithm;
    presignedURL << "&X-Amz-Credential="
                 << uriEncode(accessKey + "/" + dateStamp + "/" + region + "/" + service + "/aws4_request");
    presignedURL << "&X-Amz-Date=" << amzDate;
    presignedURL << "&X-Amz-Expires=" << expiresInSeconds;
    presignedURL << "&X-Amz-SignedHeaders=host";
    presignedURL << "&X-Amz-Signature=" << signature;

    return presignedURL.str();
}
