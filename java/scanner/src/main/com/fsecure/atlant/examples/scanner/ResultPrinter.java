package com.fsecure.atlant.examples.scanner;

import java.util.List;
import java.io.PrintStream;

class ResultPrinter
{
    PrintStream target;

    public ResultPrinter(PrintStream target) {
        this.target = target;
    }

    public void print(ScanResult result) {
        target.printf("Result: %s\n", resultToString(result.getResult()));
        List<Detection> detections = result.getDetections();
        if (!detections.isEmpty()) {
            target.println("Detections:");
            for (Detection detection : detections) {
                if (detection.getMemberName().isPresent()) {
                    target.printf("  - Name: %s; Category: %s; Member Name: %s\n",
                                  detection.getName(),
                                  categoryToString(detection.getCategory()),
                                  detection.getMemberName().get());
                } else {
                    target.printf("  - Name: %s; Category: %s\n",
                                  detection.getName(),
                                  categoryToString(detection.getCategory()));
                }
            }
        }
    }

    private String resultToString(ScanResult.Result result) {
        switch (result) {
        case CLEAN:
            return "clean";
        case WHITELISTED:
            return "whitelisted";
        case SUSPICIOUS:
            return "suspicious";
        case PUA:
            return "PUA";
        case UA:
            return "UA";
        case HARMFUL:
            return "harmful";
        default:
            throw new IllegalStateException("Invalid scan result");
        }
    }

    private String categoryToString(Detection.Category category) {
        switch (category) {
        case SUSPICIOUS:
            return "suspicious";
        case PUA:
            return "PUA";
        case UA:
            return "UA";
        case HARMFUL:
            return "harmful";
        default:
            throw new IllegalStateException("Invalid detection category");
        }
    }
}

