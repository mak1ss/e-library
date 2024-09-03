package org.library.bookservice.model.base;

public interface PrimaryEntity<T>{

    T getId();
    void setId(T id);
}
