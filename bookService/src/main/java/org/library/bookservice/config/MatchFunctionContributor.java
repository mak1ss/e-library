package org.library.bookservice.config;

import org.hibernate.boot.model.FunctionContributions;
import org.hibernate.boot.model.FunctionContributor;

public class MatchFunctionContributor implements FunctionContributor {

    @Override
    public void contributeFunctions(FunctionContributions functionContributions) {
        functionContributions.getFunctionRegistry().registerPattern(
            "match_3_columns", 
            "match(?1, ?2, ?3) against (?4 in boolean mode)"
        );
        
        System.out.println(">>> My Custom Function Contributor has been loaded! <<<");
    }
}