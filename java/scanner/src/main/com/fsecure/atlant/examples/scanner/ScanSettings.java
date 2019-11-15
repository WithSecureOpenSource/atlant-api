package com.fsecure.atlant.examples.scanner;

import java.util.Optional;

import org.json.JSONObject;

class ScanSettings
{ 
    private Optional<Boolean> scanArchives;
    private Optional<Integer> maxNested;
    private Optional<Boolean> stopOnFirst;
    private Optional<Boolean> allowUpstreamMetadata;
    private Optional<SecurityCloudSettings> securityCloudSettings;

    public ScanSettings(Optional<Boolean> scanArchives,
                        Optional<Integer> maxNested,
                        Optional<Boolean> stopOnFirst,
                        Optional<Boolean> allowUpstreamMetadata,
                        Optional<SecurityCloudSettings> securityCloudSettings) {
        this.scanArchives = scanArchives;

        if (maxNested.isPresent() && maxNested.get() < 0) {
            throw new IllegalArgumentException("maxNested must not be negative");
        }

        this.maxNested = maxNested; 
        this.stopOnFirst = stopOnFirst;
        this.allowUpstreamMetadata = allowUpstreamMetadata;
        this.securityCloudSettings = securityCloudSettings;
    }

    public Optional<Boolean> getScanArchives() {
        return scanArchives;
    }

    public Optional<Integer> getMaxNested() {
        return maxNested;
    }

    public Optional<Boolean> getStopOnFirst() {
        return stopOnFirst;
    }

    public Optional<Boolean> getAllowUpstreamMetadata() {
        return allowUpstreamMetadata;
    }

    public Optional<SecurityCloudSettings> getSecurityCloudSettings() {
        return securityCloudSettings;
    }

    protected JSONObject toJSONObject() {
        JSONObject result = new JSONObject();

        if (scanArchives.isPresent()) {
            result.put("scan_settings", scanArchives.get());
        }

        if (maxNested.isPresent()) {
            result.put("max_nested", maxNested.get());
        }

        if (stopOnFirst.isPresent()) {
            result.put("stop_on_first", stopOnFirst.get());
        }

        if (allowUpstreamMetadata.isPresent()) {
            result.put("allow_upstream_metadata", allowUpstreamMetadata.get());
        }

        if (securityCloudSettings.isPresent()) {
            result.put("security_cloud", securityCloudSettings.get().toJSONObject());
        }

        return result;
    }
}
