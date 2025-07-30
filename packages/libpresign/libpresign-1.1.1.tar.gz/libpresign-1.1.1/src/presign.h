#ifndef S3PRESIGNPYTHON_PRESIGN_H
#define S3PRESIGNPYTHON_PRESIGN_H

// #include <iostream>
#include <iomanip>
#include <sstream>
#include <openssl/hmac.h>
#include <openssl/evp.h>
#include <openssl/bio.h>
#include <openssl/buffer.h>
#include <openssl/sha.h>
#include <ctime>
#include <cstring>

std::string generatePresignedURL(const std::string& accessKey, const std::string& secretKey, const std::string& region, const std::string& bucket, const std::string& key, int expiresInSeconds, const std::string& endpoint = "s3.amazonaws.com");

#endif //S3PRESIGNPYTHON_PRESIGN_H
