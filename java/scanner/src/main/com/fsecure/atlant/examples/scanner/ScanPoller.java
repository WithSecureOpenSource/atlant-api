package com.fsecure.atlant.examples.scanner;

import java.io.IOException;
import java.io.FileNotFoundException;
import java.io.InputStream;
import java.io.FileInputStream;
import java.time.Duration;

class ScanPoller {

    private FileScanner fileScanner;

    public ScanPoller(FileScanner fileScanner) {
        this.fileScanner = fileScanner;
    }

    public ScanResult scan(ScanMetadata metadata, String path)
        throws FileNotFoundException, IOException, InterruptedException {
        return scan(metadata, new FileInputStream(path));
    }

    public ScanResult scan(ScanMetadata metadata, InputStream input)
        throws IOException, InterruptedException {
        ScanResult result = fileScanner.scan(metadata, input);

        switch (result.getStatus()) {
        case COMPLETE:
            return result;
        case PENDING:
            String pollURL = result.getPollURL().get();
            wait(result.getRetryAfter().get());

        outer:
            while (true) {
                result = fileScanner.poll(pollURL);

                switch (result.getStatus()) {
                case COMPLETE:
                    return result;
                case PENDING:
                    wait(result.getRetryAfter().get());
                    continue;
                default:
                    break outer;
                }
            }
        }

        throw new IllegalStateException("Unknown scan status");
    }

    protected void wait(Duration duration)
        throws InterruptedException {
        Thread.sleep(duration.toMillis());
    }

}

