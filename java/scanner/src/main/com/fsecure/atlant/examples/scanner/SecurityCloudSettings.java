package com.fsecure.atlant.examples.scanner;

import org.json.JSONObject;

class SecurityCloudSettings
{ 
    private boolean allowUpstreamApplicationFiles;
    private boolean allowUpstreamDataFiles;

    public SecurityCloudSettings(boolean allowUpstreamApplicationFiles,
                                 boolean allowUpstreamDataFiles) {
        this.allowUpstreamApplicationFiles = allowUpstreamApplicationFiles;
        this.allowUpstreamDataFiles = allowUpstreamDataFiles;
    }

    public boolean getAllowUpstreamApplicationFiles() {
        return allowUpstreamApplicationFiles;
    }

    public boolean allowUpstreamDataFiles() {
        return allowUpstreamDataFiles;
    }

    protected JSONObject toJSONObject() {
        JSONObject result = new JSONObject();

        result.put("allow_upstream_application_files", allowUpstreamApplicationFiles);
        result.put("allow_upstream_data_files", allowUpstreamDataFiles);

        return result;
    }
}
