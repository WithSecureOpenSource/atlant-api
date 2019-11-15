package com.fsecure.atlant.examples.scanner;

import java.util.List;
import java.util.Collections;
import java.util.Optional;
import java.time.Duration;

class ScanResult
{ 
    enum Status {
        COMPLETE,
        PENDING
    };

    enum Result {
        CLEAN,
        WHITELISTED,
        SUSPICIOUS,
        PUA,
        UA,
        HARMFUL
    };

    private Status status;
    private Result result;
    private List<Detection> detections;
    private Optional<Duration> retryAfter;
    private Optional<String> pollURL;

    public ScanResult(Status status,
                      Result result,
                      List<Detection> detections) {
        this(status, result, detections, Optional.empty(), Optional.empty());
    }
    
    public ScanResult(Status status,
                      Result result,
                      List<Detection> detections,
                      Optional<Duration> retryAfter,
                      Optional<String> pollURL) {
        this.status = status;
        this.result = result;
        this.detections = Collections.unmodifiableList(detections);
        this.retryAfter = retryAfter;
        this.pollURL = pollURL;
    }

    public Status getStatus() {
        return status;
    }

    public Result getResult() {
        return result;
    }

    public List<Detection> getDetections() {
        return detections;
    }

    public Optional<Duration> getRetryAfter() {
        return retryAfter;
    }

    public Optional<String> getPollURL() {
        return pollURL;
    }

    protected void setRetryAfter(Optional<Duration> retryAfter) {
        this.retryAfter = retryAfter;
    }

    protected void setPollURL(Optional<String> pollURL) {
        this.pollURL = pollURL;
    }
}
