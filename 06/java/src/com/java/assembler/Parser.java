package com.java.assembler;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.ArrayList;


class Parser {

    List<String> inputCleaned;
    String currentCommand;
    String commandType;
    String symbol;
    String comp;
    String dest;
    String jump;
    Integer lineCount;

    // constructor
    public Parser(String filePath) {
        try {
            // Read all input from the file and store them in the 'input' list
            Path path = Paths.get(filePath);
            // this.input = Files.readAllLines(path, StandardCharsets.UTF_8);
            inputCleaned = cleanInput(Files.readAllLines(path, StandardCharsets.UTF_8));
        }
        catch (IOException e) {
            e.printStackTrace(); // Handle or log the exception as needed
        }
        lineCount = -1;
        currentCommand = null;
    }

    public List<String> cleanInput(List<String> input) {
        if (input != null) {
            List<String> inputCleaned = new ArrayList<>();
            for (String line : input) {
                if (!line.trim().isEmpty() && !line.trim().startsWith("//")) {
                    inputCleaned.add(line.trim().replaceAll("\\s+|//(.*)", ""));
                }
            }
        return inputCleaned;
        } else {
            System.out.println("File not read or empty.");
        }
        return null;
    }

    public boolean hasMoreCommands() {
        if (inputCleaned.size() - 1 > lineCount) {
            return true;
        }
        return false;
    }

    public void advance() {
        lineCount++;
        currentCommand = this.inputCleaned.get(lineCount);
    }

    public void getCommandType() {
        if (currentCommand.startsWith("(")) {
            commandType = "L_COMMAND";
        } else if (currentCommand.startsWith("@")) {
            commandType = "A_COMMAND";
        } else {
            commandType = "C_COMMAND";
        }
    }

    public void getSymbol() {
        if (currentCommand.startsWith("(")) {
            symbol = currentCommand.replaceAll("(|)", "");
        } else if (currentCommand.startsWith("@")) {
            symbol = currentCommand.replace("@", "");
        }
    }

    public void displayFileContent() {
        if (inputCleaned != null) {
            for (String line : inputCleaned) {
                System.out.println(line);
            }
        } else {
            System.out.println("File not read or empty.....");
        }
    }

    public void resetValues() {
        symbol = null;
        comp = null;
        dest = null;
        jump = null;
    }

    public void parseACommand() {
        symbol = currentCommand.replace("@", "");
    }

    public void parseLCommand() {
        symbol = currentCommand.replaceAll("[()]", "");
    }

    public void parseCCommand() {
        String[] parts = currentCommand.split("=");

        // if there is a destination
        if (parts.length == 2) {
            dest = parts[0];
        }

        // use first element of array as nothing was split if "=" not in string
        String[] remainder = parts[0].split(";");

        if (remainder.length == 2) {
            comp = remainder[0];
            jump = remainder[1];
        } else {
            // if ";" not in string then just use first element in array
            comp = parts[1];
        }

    }

    public static void main(String[] args) {
        // Example usage
        Parser parser = new Parser("../../add/Add.asm");
        parser.displayFileContent();

        System.out.println("\n");

        while (parser.hasMoreCommands()) {

            parser.advance();

            parser.getCommandType();

            if (parser.commandType.equals("A_COMMAND")) {
                parser.parseACommand();
            }
            if (parser.commandType.equals("L_COMMAND")) {
                parser.parseLCommand();
            }
            if (parser.commandType.equals("C_COMMAND")) {
                parser.parseCCommand();
            }  

            System.out.println(parser.currentCommand);
            System.out.println(parser.commandType);
            System.out.println(parser.symbol);
            System.out.println(parser.dest);
            System.out.println(parser.comp);
            System.out.println(parser.jump);
            System.out.println("\n");

            parser.resetValues();

        }
    }
}