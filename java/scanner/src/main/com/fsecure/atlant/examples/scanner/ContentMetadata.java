package com.fsecure.atlant.examples.scanner;

import java.util.Optional;

import org.json.JSONObject;

class ContentMetadata
{ 
    private Optional<String> SHA1;
    private Optional<String> URI;
    private Optional<Integer> contentLength;
    private Optional<String> contentType;
    private Optional<String> charset;

    public ContentMetadata(Optional<String> SHA1,
                            Optional<String> URI,
                            Optional<Integer> contentLength,
                            Optional<String> contentType,
                            Optional<String> charset) {
        this.SHA1 = SHA1;
        this.URI = URI;
        this.contentLength = contentLength;
        this.contentType = contentType;
        this.charset = charset;
    }

    public Optional<String> getSHA1() {
        return SHA1;
    }

    public Optional<String> getURI() {
        return URI;
    }

    public Optional<Integer> getContentLength() {
        return contentLength;
    }

    public Optional<String> getContentType() {
        return contentType;
    }

    public Optional<String> getCharset() {
        return charset;
    }

    protected JSONObject toJSONObject() {
        JSONObject result = new JSONObject();

        if (SHA1.isPresent()) {
            result.put("sha1", SHA1.get());
        }

        if (URI.isPresent()) {
            result.put("uri", URI.get());
        }

        if (contentLength.isPresent()) {
            result.put("content_length", contentLength.get());
        }

        if (contentType.isPresent()) {
            result.put("content_type", contentType.get());
        }

        if (charset.isPresent()) {
            result.put("charset", charset.get());
        }

        return result;
    }

}
