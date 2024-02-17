package com.java.assembler;

import java.util.HashMap;

class Code {

    HashMap<String, String> compMnemonics;
    HashMap<String, String> destMnemonics;
    HashMap<String, String> jumpMnemonics;

    public Code() {
        compMnemonics = new HashMap<>();
        destMnemonics = new HashMap<>();
        jumpMnemonics = new HashMap<>();

        popluateCompMnemonics();
        populateDestMnemonics();
        populateJumpMnemonics();
    }

    public void popluateCompMnemonics() {
        compMnemonics.put("0", "0101010");
        compMnemonics.put("1", "0111111");
        compMnemonics.put("-1", "0111010");
        compMnemonics.put("D", "0001100");
        compMnemonics.put("A", "0110000");
        compMnemonics.put("M", "1110000");
        compMnemonics.put("!D", "0001101");
        compMnemonics.put("!A", "0110001");
        compMnemonics.put("!M", "1110001");
        compMnemonics.put("-D", "0001111");
        compMnemonics.put("-A", "0110011");
        compMnemonics.put("-M", "1110011");
        compMnemonics.put("D+1", "0011111");
        compMnemonics.put("A+1", "0110111");
        compMnemonics.put("M+1", "1110111");
        compMnemonics.put("D-1", "0001110");
        compMnemonics.put("A-1", "0110010");
        compMnemonics.put("M-1", "1110010");
        compMnemonics.put("D+A", "0000010");
        compMnemonics.put("D+M", "1000010");
        compMnemonics.put("D-A", "0010011");
        compMnemonics.put("D-M", "1010011");
        compMnemonics.put("A-D", "0000111");
        compMnemonics.put("M-D", "1000111");
        compMnemonics.put("D&A", "0000000");
        compMnemonics.put("D&M", "1000000");
        compMnemonics.put("D|A", "0010101");
        compMnemonics.put("D|M", "1010101");
    }

    public void populateJumpMnemonics() {
        jumpMnemonics.put("NULL", "000");
        jumpMnemonics.put("JGT", "001");
        jumpMnemonics.put("JEQ", "010");
        jumpMnemonics.put("JGE", "011");
        jumpMnemonics.put("JLT", "100");
        jumpMnemonics.put("JNE", "101");
        jumpMnemonics.put("JLE", "110");
        jumpMnemonics.put("JMP", "111");
	}

    public void populateDestMnemonics() {
        destMnemonics.put("NULL", "000");
        destMnemonics.put("M", "001");
        destMnemonics.put("D", "010");
        destMnemonics.put("MD", "011");
        destMnemonics.put("A", "100");
        destMnemonics.put("AM", "101");
        destMnemonics.put("AD", "110");
        destMnemonics.put("AMD", "111");
    }

    public String comp(String mnemonic) {
        if (mnemonic == null || mnemonic.isEmpty()) {
            mnemonic = "NULL";
        }
        
        return compMnemonics.get(mnemonic);
    }

    public String dest(String mnemonic) {
        if (mnemonic == null || mnemonic.isEmpty()) {
            mnemonic = "NULL";
        }
        
        return destMnemonics.get(mnemonic);
    }

    public String jump(String mnemonic) {
        if (mnemonic == null || mnemonic.isEmpty()) {
            mnemonic = "NULL";
        }
        
        return jumpMnemonics.get(mnemonic);
    }

    public String convertToBinary(String number) {
        // Convert the input string to an integer
        int value = Integer.parseInt(number);

        // Convert the integer value to its binary representation as a string
        String binaryNumber = Integer.toBinaryString(value);

        // Format the binary number by adding leading zeros to make it 15 characters long
        // If the binary number is shorter than 15 characters, it pads with leading zeros
        String formattedBinaryNumber = String.format("%15s", binaryNumber).replace(' ', '0');

        return formattedBinaryNumber;
    }
}