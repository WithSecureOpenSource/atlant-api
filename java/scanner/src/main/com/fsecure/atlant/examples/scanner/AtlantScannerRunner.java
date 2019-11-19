package com.fsecure.atlant.examples.scanner;

import java.util.Set;

class AtlantScannerRunner
{ 
    public static void main(String args[]) 
    { 
        CommandLine commandLine = null;
        try {
            commandLine = new CommandLine(args);
        } catch (InvalidInvocationException e) {
            System.err.printf("Invalid usage: %s\n", e.getMessage());
            System.err.println(CommandLine.USAGE);
            System.exit(1);
        }

        Authenticator authenticator =
            new Authenticator(commandLine.getAuthorizationAddress(),
                              commandLine.getClientID(),
                              commandLine.getClientSecret(),
                              Set.of("scan"));

        ScanMetadata metadata = new ScanMetadata();

        try {
            FileScanner fileScanner = new FileScanner(commandLine.getScanAddress(),
                                                      authenticator);
            ScanPoller scanPoller = new ScanPoller(fileScanner);

            ScanResult result = scanPoller.scan(metadata,
                                                commandLine.getInputFile());

            ResultPrinter printer = new ResultPrinter(System.out);
            printer.print(result);
        } catch (Throwable e) {
            System.err.format("Error: %s\n", e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    } 
}
