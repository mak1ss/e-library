package org.library.bookservice.filtering;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public enum FilteringOperation {

    EQUAL("="),
    NOT_EQUAL("!="),

    CONTAIN(":"),

    GREATER_THEN(">"),
    GREATER_OR_EQUAL(">="),

    LESS_THEN("<"),
    LESS_OR_EQUAL("<="),

    IN("_="),
    NOT_IN("!_=");

    private final String value;

    public static FilteringOperation fromString(String text) {
        for (FilteringOperation b : FilteringOperation.values()) {
            if (b.value.equalsIgnoreCase(text)) {
                return b;
            }
        }
        throw new UnsupportedOperationException("Unknown filtering operation '" + text + "'");
    }
}
