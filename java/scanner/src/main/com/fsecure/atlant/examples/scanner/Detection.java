package com.fsecure.atlant.examples.scanner;

import java.util.Optional;

class Detection
{
    enum Category {
        SUSPICIOUS,
        PUA,
        UA,
        HARMFUL
    };

    private Category category;
    private String name;
    private Optional<String> memberName;

    public Detection(Category category, String name, Optional<String> memberName) {
        this.category = category;
        this.name = name;
        this.memberName = memberName;
    }

    public Category getCategory() {
        return category;
    }

    public String getName() {
        return name;
    }

    public Optional<String> getMemberName() {
        return memberName;
    }
}
