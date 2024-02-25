package com.java.assembler;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

class Assembler {

    Code code;
    Parser parser;
    SymbolTable symbolTable;
    String outputPath;

    public Assembler(String filePath) {
        this.parser = new Parser(filePath);
        this.code = new Code();
        this.symbolTable = new SymbolTable();
        this.outputPath = filePath.replace(".asm", ".hack");
    }

    private void writeToFile(List<String> outputCommands) {
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(outputPath))) {
            // Writing each line to the file
            for (String line : outputCommands) {
                writer.write(line);
                writer.newLine(); // Add a newline after each line
            }

            System.out.println("File has been written successfully.");

        } catch (IOException e) {
            System.err.println("Error writing to the file: " + e.getMessage());
        }
    }

    public static void main(String[] args) {
        
        Assembler assembler = new Assembler(args[0]);

        String cc = null;
        String dd = null;
        String jj = null;
        String command = null;
        List<String> outputCommands = new ArrayList<>();

        Integer numberOfLabelsAdded = 0;

        // first pass
        while (assembler.parser.hasMoreCommands()) {


            assembler.parser.advance();

            assembler.parser.getCommandType();

            if (assembler.parser.commandType.equals("L_COMMAND")) {

                assembler.parser.parseLCommand();
                assembler.symbolTable.addSymbol(
                    assembler.parser.symbol, 
                    Integer.toString(assembler.parser.lineCount - numberOfLabelsAdded)
                );

                numberOfLabelsAdded++;
            }
        }

        System.out.println("SymbolTable contents: ");

        for (Map.Entry<String, String> entry : assembler.symbolTable.symbolTable.entrySet()) {
            System.out.println("Symbol: " + entry.getKey() + ", Address: " + entry.getValue());
        }

        assembler.parser.resetLineCount();

        // second pass
        while (assembler.parser.hasMoreCommands()) {

            assembler.parser.advance();

            assembler.parser.getCommandType();

            if (assembler.parser.commandType.equals("A_COMMAND")) {
                assembler.parser.parseACommand();

                // if A_COMMAND like @123
                if (assembler.parser.symbol.matches("\\d+")) {
                    command = "0" + assembler.code.convertToBinary(assembler.parser.symbol);
                } else if (assembler.symbolTable.symbolTable.containsKey(assembler.parser.symbol)) {
                    String address = assembler.symbolTable.getSymbol(assembler.parser.symbol);
                    command = "0" + assembler.code.convertToBinary(address); 
                } else {
                    assembler.symbolTable.addSymbol(
                        assembler.parser.symbol, 
                        Integer.toString(assembler.symbolTable.memoryAddressCount)
                    );
                    command = "0" + assembler.code.convertToBinary(
                        Integer.toString(assembler.symbolTable.memoryAddressCount)
                    );
                    assembler.symbolTable.memoryAddressCount++;
                }
            }

            if (assembler.parser.commandType.equals("L_COMMAND")) {
                assembler.parser.parseLCommand();
            }

            if (assembler.parser.commandType.equals("C_COMMAND")) {
                assembler.parser.parseCCommand();

                cc = assembler.code.comp(assembler.parser.comp);
                dd = assembler.code.dest(assembler.parser.dest);
                jj = assembler.code.jump(assembler.parser.jump);
                
                command = "111" + cc + dd + jj;
            }

            System.out.println(assembler.parser.currentCommand);
            System.out.println(assembler.parser.commandType);
            System.out.println(assembler.parser.symbol);
            System.out.println(assembler.parser.comp);
            System.out.println(cc);
            System.out.println(assembler.parser.dest);
            System.out.println(dd);
            System.out.println(assembler.parser.jump);
            System.out.println(jj);

            // if (assembler.parser.commandType.equals("C_COMMAND")) {
                
            // }
            if (command != null) {
                System.out.println("Command: " + command);
                outputCommands.add(command);
            }
            System.out.println("\n");

            assembler.parser.resetValues();
            cc = null;
            dd = null;
            jj = null;
            command = null;

        }

        assembler.writeToFile(outputCommands);

    }
}
