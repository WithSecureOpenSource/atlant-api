package com.fsecure.atlant.examples.scanner;

import java.util.Optional;

import org.json.JSONObject;

class ScanMetadata
{ 
    private Optional<ScanSettings> scanSettings;
    private Optional<ContentMetadata> contentMetadata;

    public ScanMetadata() {
        this(Optional.empty(), Optional.empty());
    }

    public ScanMetadata(Optional<ScanSettings> scanSettings,
                        Optional<ContentMetadata> contentMetadata) {
        this.scanSettings = scanSettings;
        this.contentMetadata = contentMetadata;
    }

    public Optional<ScanSettings> getScanSettings() {
        return scanSettings;
    }

    public Optional<ContentMetadata> getContentMetadata() {
        return contentMetadata;
    }

    protected JSONObject toJSONObject() {
        JSONObject result = new JSONObject();

        if (scanSettings.isPresent()) {
            result.put("scan_settings", scanSettings.get().toJSONObject());
        }

        if (contentMetadata.isPresent()) {
            result.put("content_meta", contentMetadata.get().toJSONObject());
        }

        return result;
    }
}
