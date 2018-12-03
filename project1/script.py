
# @description Computer Architecture Project 1 - MIPS Disassembler
# @author Alex Pereira

import math 

# @description Main code 
def main():
    instructions = [0x032BA020, 0x8CE90014, 0x12A90003, 0x022DA822, 0xADB30020, 0x02697824, 0xAE8FFFF4, 0x018C6020, 0x02A4A825, 0x158FFFF7, 0x8ECDFFF0]
    
    output = disassemble(instructions)
    
    writeFile(output)

# @description Disassemble instructions
# @param {hex[]} instructions
# @return {string[]}
def disassemble(instructions):

    # Disassemble masks - ref: DisassembleMasks_Student.xlsx
    maskS1 = 0x03E00000
    maskS2Dst = 0x001F0000
    maskDst = 0x0000F800
    maskFunc = 0x0000003F
    maskOpCode = 0xFC000000
    maskOffset = 0x0000FFFF

    rOpCode = 0x00

    # Initial instruction address
    initAddress = 0x9A040

    for i, instruction in enumerate(instructions):

        # Get current address - increment by 4 bits @ each iteration
        address = initAddress + (i * 4)

        # Get opcode from instruction
        opcode = instruction & maskOpCode
        opcode = opcode >> 26

        # Get source from instruction
        source = instruction & maskS1
        source = source >> 21
        source = str(int(hex(source), 16)) 

        # Get target from instruction
        target = instruction & maskS2Dst
        target = target >> 16
        target = str(int(hex(target), 16))

        # Get destination from instruction
        destination = instruction & maskDst
        destination = destination >> 11
        destination = str(int(hex(destination), 16))

        # Get offset from instruction
        offset = instruction & maskOffset

        # Get function from instruction - assign to opcode (for simplicity)
        if opcode == rOpCode:
            opcode = instruction & maskFunc

        # Put back disassembled instruction
        instructions[i] = buildLine(address, opcode, source, target, destination, offset)

    return instructions

'''
@description Build output message in the formats:
    
    ADD destination, source, target
    SUB destination, source, target
    AND destination, source, target
    OR destination, source, target
    SLT destination, source, target

    LW target, offset(source)
    SW target, offset(source)
    BEQ source, target, branch address
    BNE source, target, branch address

@param {hex} address
@param {hex} opcode
@param {string} source
@param {string} target
@param {string} destination
@param {hex} offset
@return {string} 
'''
def buildLine(address, opcode, source, target, destination, offset):

    # Parse negative offsets
    if offset >= math.pow(2, 6):
        offset = -int(round(math.pow(2, 16) - offset))

    # Instruction codes
    ADD, SUB, AND, OR, SLT = 0x20, 0x22, 0x24, 0x25, 0x2A
    LW, SW, BEQ, BNE = 0x23, 0x2B, 0x04, 0x05

    line = ''

    if opcode == ADD:
        line = hex(address)[2:] + '\t ADD \t$' + destination + ', \t$' + source + ', \t$' + target

    elif opcode == SUB:
        line = hex(address)[2:] + '\t SUB \t$' + destination + ', \t$' + source + ', \t$' + target

    elif opcode == AND:
        line = hex(address)[2:] + '\t AND \t$' + destination + ', \t$' + source + ', \t$' + target

    elif opcode == OR:
        line = hex(address)[2:] + '\t OR \t$' + destination + ', \t$' + source + ', \t$' + target

    elif opcode == SLT:
        line = hex(address)[2:] + '\t SLT \t$' + destination + ', \t$' + source + ', \t$' + target

    elif opcode == LW:
        line = hex(address)[2:] + '\t LW \t$' + target + ', \t' + str(offset) + '($' + source + ')'

    elif opcode == SW:
        line = hex(address)[2:] + '\t SW \t$' + target + ', \t' + str(offset) + '($' + source + ')'

    elif opcode == BEQ:
        branchAddress = (offset << 2) + address
        line = hex(address)[2:] + '\t BEQ \t$' + source + ', \t$' + target + ', \taddress ' + hex(branchAddress)[2:]

    elif opcode == BNE:
        branchAddress = (offset << 2) + address
        line = hex(address)[2:] + '\t BNE \t$' + source + ', \t$' + target + ', \taddress ' + hex(branchAddress)[2:]

    return line

# @description Write output to file
# @param {string[]} output 
def writeFile(output):
    
    file = open('output.txt', 'w+')

    for instruction in output:
        file.write('%s\r\n' % instruction)
    file.close()

if __name__ == '__main__':
    main()