package com.fsecure.atlant.examples.scanner;

import java.util.List;
import java.util.ArrayList;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.stream.Stream; 
import java.util.stream.Collectors;
import java.util.Random;
import java.util.Iterator;

class MultiPartBuilder
{ 
    private static final int BOUNDARY_BYTES = 32;

    static class Part {
        private String name;
        private String contentType;
        private byte[] content;

        public Part(String name, String contentType, byte[] content) {
            this.name = name;
            this.contentType = contentType;
            this.content = content;
        }

        public Part(String name, String contentType, InputStream content)
            throws IOException {
            this(name, contentType, content.readAllBytes());
        }

        private byte[] encode() throws IOException {
            ByteArrayOutputStream buffer = new ByteArrayOutputStream();
            String escapedName = this.name.replace("\"", "\\\"");
            String contentDisposition =
                String.format("Content-Disposition: form-data; name=\"%s\"\r\n", escapedName);
            String contentType =
                String.format("Content-Type: %s\r\n\r\n", this.contentType);
            buffer.write(contentDisposition.getBytes(StandardCharsets.UTF_8));
            buffer.write(contentType.getBytes(StandardCharsets.UTF_8));
            buffer.write(this.content);
            return buffer.toByteArray();
        }

        public String getName() {
            return name;
        }

        public String getContentType() {
            return contentType;
        }

        public byte[] getContent() {
            return content;
        }
    }

    private List<Part> parts;
    private String boundary;

    public MultiPartBuilder() {
        parts = new ArrayList<Part>();
        boundary = makeBoundary();
    }

    public MultiPartBuilder addPart(Part part) {
        parts.add(part);
        return this;
    }

    public byte[] encode() throws IOException {
        byte[] initiator =
            String.format("--%s\r\n", boundary).getBytes(StandardCharsets.UTF_8);
        byte[] terminator =
            String.format("\r\n--%s--\r\n", boundary).getBytes(StandardCharsets.UTF_8);
        byte[] separator =
           String.format("\r\n--%s\r\n", boundary).getBytes(StandardCharsets.UTF_8);

        ByteArrayOutputStream buffer = new ByteArrayOutputStream();
        buffer.write(initiator);
        
        Iterator<Part> iter = parts.iterator();
        while (iter.hasNext()) {
            buffer.write(iter.next().encode());
            if (iter.hasNext()) {
                buffer.write(separator);
            }
        }

        buffer.write(terminator);

        return buffer.toByteArray();
    }

    public String getBoundary() {
        return boundary;
    }

    private String makeBoundary() {
        byte[] bytes = new byte[BOUNDARY_BYTES];
        new Random().nextBytes(bytes);

        StringBuilder boundary = new StringBuilder();
        boundary.append("Boundary");
        for (byte b : bytes) {
            boundary.append(String.format("%02x", b));
        }

        return boundary.toString();
    }
}
