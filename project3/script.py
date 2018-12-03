# @description Computer Architecture Project 3 - Final Lab Assignment
# @author Alex Pereira

import math 
import copy

# Global pipeline registers and fake program counter
nop = 0x0
pipRegs = {}
fakePC = 0x7A000
clockCycle = 1

# @description Main code 
def main():
  global pipRegs
  global clockCycle
  global fakePC

  # Test Instructions
  instructions = [0xa1020000, 0x810AFFFC, 0x00831820, 0x01263820, 0x01224820, 0x81180000, 0x81510010, 0x00624022, 0x00000000, 0x00000000, 0x00000000, 0x00000000]

  # Initialization code
  Main_Mem = initMem(1024, 255)
  Regs = initRegs()
  pipRegs = {
    'IF/ID': { 'Write': PipelineRegister(), 'Read': PipelineRegister() },
    'ID/EX': { 'Write': PipelineRegister(), 'Read': PipelineRegister() },
    'EX/MEM': { 'Write': PipelineRegister(), 'Read': PipelineRegister() },
    'MEM/WB': { 'Write': PipelineRegister(), 'Read': PipelineRegister() }
  }

  # Pipeline loop
  for instruction in instructions:
    IF_stage(instruction)
    ID_stage(Regs)
    EX_stage()
    MEM_stage(Main_Mem)
    WB_stage(Regs)
    Print_out_everything(Regs)
    Copy_write_to_read()

    clockCycle += 1
    fakePC += 4

# @description Initialize main memory
# @param {number} size
# @param {number} cap
# @returns {array} mem
def initMem(size, cap):
  mem = []
  for i in range(size):
    mem.append(i % (cap + 1))
  return mem

# @description Initialize registers
# @returns {array} regs
def initRegs():
  regs = [0]
  for i in range(1, 32):
    regs.append(0x100 + i)
  return regs

# @description Pipeline register class
class PipelineRegister:
  def __init__(self):
    self.reset()

  def reset(self):
    self.Inst = nop
    self.IncrPC = nop
    self.Control = {
      'RegDst': 0,
      'ALUSrc': 0,
      'MemToReg': 0,
      'RegWrite': 0,
      'MemRead': 0,
      'MemWrite': 0,
      'Branch': 0,
      'ALUOp1': 0,
      'ALUOp0': 0
    }
    self.ReadReg1Value = nop
    self.ReadReg2Value = nop
    self.SEOffset = nop
    self.WriteReg_20_16 = None
    self.WriteReg_15_11 = None
    self.Function = nop
    self.CalcBTA = None
    self.Zero = False
    self.ALUResult = nop
    self.SWValue = nop
    self.LWDataValue = nop
    self.WriteRegNum = None

# @description Instruction fetch stage
# @param {hex} instruction
def IF_stage(instruction):
  global pipRegs

  # Set pipRegs['IF/ID']['Write']
  if instruction != nop:
    pipRegs['IF/ID']['Write'].Inst = instruction
    pipRegs['IF/ID']['Write'].IncrPC = fakePC
  else:
    # Reset pipRegs['IF/ID']['Write']
    pipRegs['IF/ID']['Write'].reset()

# @description Instruction decode and register file read
# @param {array} Regs
def ID_stage(Regs):
  global pipRegs

  # Instruction codes
  lb, sb, add, sub = 0x20, 0x28, 0x20, 0x22

  # Get instruction from IF/ID Read
  instruction = pipRegs['IF/ID']['Read'].Inst

  # Decode instruction
  opcode = (instruction & 0xFC000000) >> 26
  source = (instruction & 0x03E00000) >> 21
  target = (instruction & 0x001F0000) >> 16
  destin = (instruction & 0x0000F800) >> 11

  offset = instruction & 0x0000FFFF
  function = instruction & 0x0000003F

  # Set pipRegs['ID/EX']['Write']
  if instruction != nop:
    pipRegs['ID/EX']['Write'].Control['RegDst'] = 1 if opcode == nop else 0
    pipRegs['ID/EX']['Write'].Control['ALUSrc'] = 1 if opcode == lb or opcode == sb else 0
    pipRegs['ID/EX']['Write'].Control['ALUOp1'] = 1 if opcode == nop else 0
    pipRegs['ID/EX']['Write'].Control['ALUOp0'] = 1 if opcode == nop and lb == nop and sb == nop else 0
    pipRegs['ID/EX']['Write'].Control['MemRead'] = 1 if opcode == lb else 0
    pipRegs['ID/EX']['Write'].Control['MemWrite'] = 1 if opcode == sb else 0
    pipRegs['ID/EX']['Write'].Control['Branch'] = 1 if opcode == nop and lb == nop and sb == nop else 0
    pipRegs['ID/EX']['Write'].Control['MemToReg'] = 1 if opcode == lb else 0
    pipRegs['ID/EX']['Write'].Control['RegWrite'] = 1 if opcode == nop or opcode == lb else 0

    pipRegs['ID/EX']['Write'].IncrPC = pipRegs['IF/ID']['Read'].IncrPC
    pipRegs['ID/EX']['Write'].ReadReg1Value = Regs[int(source)]
    pipRegs['ID/EX']['Write'].ReadReg2Value = Regs[int(target)]
    pipRegs['ID/EX']['Write'].SEOffset = sign_extend(offset)
    pipRegs['ID/EX']['Write'].WriteReg_20_16 = int(target)
    pipRegs['ID/EX']['Write'].WriteReg_15_11 = int(destin)
    pipRegs['ID/EX']['Write'].Function = hex(function)
    
  else:
    # Reset pipRegs['ID/EX']['Write']
    pipRegs['ID/EX']['Write'].reset()

# @description Execute or address calculation
def EX_stage():
  global pipRegs

  # Copy ID/EX Read register into EX/MEM Write register
  pipRegs['EX/MEM']['Write'] = copy.deepcopy(pipRegs['ID/EX']['Read'])

  # Set ALUResult
  if pipRegs['EX/MEM']['Write'].Control['ALUSrc'] == 0:
    pipRegs['EX/MEM']['Write'].ALUResult = pipRegs['EX/MEM']['Write'].ReadReg1Value + pipRegs['EX/MEM']['Write'].ReadReg2Value
  else:
    pipRegs['EX/MEM']['Write'].ALUResult = int(pipRegs['EX/MEM']['Write'].ReadReg1Value + twos_complement(pipRegs['EX/MEM']['Write'].SEOffset))

  # Set SWValue
  pipRegs['EX/MEM']['Write'].SWValue = pipRegs['ID/EX']['Read'].ReadReg2Value
  
  # Set WriteRegNum
  if pipRegs['EX/MEM']['Write'].Control['RegDst'] == 1:
    pipRegs['EX/MEM']['Write'].WriteRegNum = pipRegs['EX/MEM']['Write'].WriteReg_15_11
  else:
    pipRegs['EX/MEM']['Write'].WriteRegNum = pipRegs['EX/MEM']['Write'].WriteReg_20_16

# @description Memory access
# @param {array} Main_Mem
def MEM_stage(Main_Mem):
  global pipRegs

  # Copy ID/EX Read register into EX/MEM Write register
  pipRegs['MEM/WB']['Write'] = copy.deepcopy(pipRegs['EX/MEM']['Read'])

  # Set LWDataValue
  if pipRegs['MEM/WB']['Write'].Control['MemToReg'] == 1:
    pipRegs['MEM/WB']['Write'].LWDataValue = Main_Mem[pipRegs['MEM/WB']['Write'].ALUResult]

  # Write to Memory
  if pipRegs['MEM/WB']['Write'].Control['MemWrite'] == 1:
    print '\n\n\n\n Main_Mem (BEFORE): ', Main_Mem
    Main_Mem[pipRegs['MEM/WB']['Write'].ALUResult] = pipRegs['MEM/WB']['Write'].SWValue
    print '\n\n\n\n Main_Mem (AFTER): ', Main_Mem

# @description Write-back
# @param {array} Regs
def WB_stage(Regs):
  global pipRegs

  # Write to Registers
  if pipRegs['MEM/WB']['Read'].Control['RegWrite']:
    if pipRegs['MEM/WB']['Read'].Control['MemToReg'] == 0:
      Regs[int(pipRegs['MEM/WB']['Read'].WriteRegNum)] = pipRegs['MEM/WB']['Read'].ALUResult
    else:
      Regs[int(pipRegs['MEM/WB']['Read'].WriteRegNum)] = pipRegs['MEM/WB']['Read'].LWDataValue

# @description Print out everything
# @param {array} Regs
def Print_out_everything(Regs):
  global pipRegs

  print '\n\n\n', '# CLOCK CYCLE ', clockCycle, '\n'

  print 'Registers \n', ''.join([ '\t$' + str(i) + ': ' + hex(reg) + ('\n' if i%8 == 0 else '') for i, reg in enumerate(Regs)])

  print '\nIF/ID Write (written to by the IF stage)'
  print 'Inst = ', hex(pipRegs['IF/ID']['Write'].Inst), '\t', 'IncrPC = ', hex(pipRegs['IF/ID']['Write'].IncrPC), '\n', 
  
  print '\nIF/ID Read (read by the ID stage)'
  print 'Inst = ', hex(pipRegs['IF/ID']['Read'].Inst), '\t', 'IncrPC = ', hex(pipRegs['IF/ID']['Read'].IncrPC), '\n', 
  
  print '\nID/EX Write (written to by the ID stage)'
  print 'Control: ' \
  'RegDst = ', pipRegs['ID/EX']['Write'].Control['RegDst'], '\t' \
  'ALUSrc = ', pipRegs['ID/EX']['Write'].Control['ALUSrc'], '\t' \
  'ALUOp = ', pipRegs['ID/EX']['Write'].Control['ALUOp1'], pipRegs['ID/EX']['Write'].Control['ALUOp0'], '\t' \
  'MemRead = ', pipRegs['ID/EX']['Write'].Control['MemRead'], '\t' \
  'MemWrite = ', pipRegs['ID/EX']['Write'].Control['MemWrite'], '\t' \
  'Branch = ', pipRegs['ID/EX']['Write'].Control['Branch'], '\t' \
  'MemToReg = ', pipRegs['ID/EX']['Write'].Control['MemToReg'], '\t' \
  'RegWrite = ', pipRegs['ID/EX']['Write'].Control['RegWrite']
  print 'IncrPC = ', hex(pipRegs['ID/EX']['Write'].IncrPC), '\t', 'ReadReg1Value = ', hex(pipRegs['ID/EX']['Write'].ReadReg1Value), '\t', 'ReadReg2Value = ', hex(pipRegs['ID/EX']['Write'].ReadReg2Value)
  print 'SEOffset = ', pipRegs['ID/EX']['Write'].SEOffset, '\t', 'WriteReg_20_16 = ', pipRegs['ID/EX']['Write'].WriteReg_20_16, '\t', 'WriteReg_15_11 = ', pipRegs['ID/EX']['Write'].WriteReg_15_11, '\t', 'Function = ', pipRegs['ID/EX']['Write'].Function
  
  print '\nID/EX Read (read by the EX stage)'
  print 'Control: ' \
  'RegDst = ', pipRegs['ID/EX']['Read'].Control['RegDst'], '\t' \
  'ALUSrc = ', pipRegs['ID/EX']['Read'].Control['ALUSrc'], '\t' \
  'ALUOp = ', pipRegs['ID/EX']['Read'].Control['ALUOp1'] , pipRegs['ID/EX']['Read'].Control['ALUOp0'], '\t' \
  'MemRead = ', pipRegs['ID/EX']['Read'].Control['MemRead'], '\t' \
  'MemWrite = ', pipRegs['ID/EX']['Read'].Control['MemWrite'], '\t' \
  'Branch = ', pipRegs['ID/EX']['Read'].Control['Branch'], '\t' \
  'MemToReg = ', pipRegs['ID/EX']['Read'].Control['MemToReg'], '\t' \
  'RegWrite = ', pipRegs['ID/EX']['Read'].Control['RegWrite']
  print 'IncrPC = ', hex(pipRegs['ID/EX']['Read'].IncrPC), '\t', 'ReadReg1Value = ', hex(pipRegs['ID/EX']['Read'].ReadReg1Value), '\t', 'ReadReg2Value = ', hex(pipRegs['ID/EX']['Read'].ReadReg2Value)
  print 'SEOffset = ', pipRegs['ID/EX']['Read'].SEOffset, '\t', 'WriteReg_20_16 = ', pipRegs['ID/EX']['Read'].WriteReg_20_16, '\t', 'WriteReg_15_11 = ', pipRegs['ID/EX']['Read'].WriteReg_15_11, '\t', 'Function = ', pipRegs['ID/EX']['Read'].Function
  
  print '\nEX/MEM Write (written to by the EX stage)'
  print 'Control: ' \
  'MemRead = ', pipRegs['EX/MEM']['Write'].Control['MemRead'], '\t' \
  'MemWrite = ', pipRegs['EX/MEM']['Write'].Control['MemWrite'], '\t' \
  'Branch = ', pipRegs['EX/MEM']['Write'].Control['Branch'], '\t' \
  'MemToReg = ', pipRegs['EX/MEM']['Write'].Control['MemToReg'], '\t' \
  'RegWrite = ', pipRegs['EX/MEM']['Write'].Control['RegWrite']
  # See NOTE
  # print 'CalcBTA = ', pipRegs['EX/MEM']['Write'].CalcBTA, '\t', 'Zero = ', pipRegs['EX/MEM']['Write'].Zero, '\t', 'ALUResult = ', hex(pipRegs['EX/MEM']['Write'].ALUResult)
  print 'ALUResult = ', hex(pipRegs['EX/MEM']['Write'].ALUResult)
  print 'SWValue = ', hex(pipRegs['EX/MEM']['Write'].SWValue), '\t', 'WriteRegNum = ', pipRegs['EX/MEM']['Write'].WriteRegNum
  
  print '\nEX/MEM Read (read by the MEM stage)'
  print 'Control: ' \
  'MemRead = ', pipRegs['EX/MEM']['Read'].Control['MemRead'], '\t' \
  'MemWrite = ', pipRegs['EX/MEM']['Read'].Control['MemWrite'], '\t' \
  'Branch = ', pipRegs['EX/MEM']['Read'].Control['Branch'], '\t' \
  'MemToReg = ', pipRegs['EX/MEM']['Read'].Control['MemToReg'], '\t' \
  'RegWrite = ', pipRegs['EX/MEM']['Read'].Control['RegWrite']
  # See NOTE
  # print 'CalcBTA = ', pipRegs['EX/MEM']['Read'].CalcBTA, '\t', 'Zero = ', pipRegs['EX/MEM']['Read'].Zero, '\t', 'ALUResult = ', hex(pipRegs['EX/MEM']['Read'].ALUResult)
  print 'ALUResult = ', hex(pipRegs['EX/MEM']['Read'].ALUResult)
  print 'SWValue = ', hex(pipRegs['EX/MEM']['Read'].SWValue), '\t', 'WriteRegNum = ', pipRegs['EX/MEM']['Read'].WriteRegNum
  
  print '\nMEM/WB Write (written to by the MEM stage)'
  print 'Control: ' \
  'MemToReg = ', pipRegs['MEM/WB']['Write'].Control['MemToReg'], '\t' \
  'RegWrite = ', pipRegs['MEM/WB']['Write'].Control['RegWrite']
  print 'LWDataValue = ', hex(pipRegs['MEM/WB']['Write'].LWDataValue), '\t', 'ALUResult = ', hex(pipRegs['MEM/WB']['Write'].ALUResult), '\t', 'WriteRegNum = ', pipRegs['MEM/WB']['Write'].WriteRegNum
  
  print '\nMEM/WB Read (read by the WB stage)'
  print 'Control: ' \
  'MemToReg = ', pipRegs['MEM/WB']['Read'].Control['MemToReg'], '\t' \
  'RegWrite = ', pipRegs['MEM/WB']['Read'].Control['RegWrite']
  print 'LWDataValue = ', hex(pipRegs['MEM/WB']['Read'].LWDataValue), '\t', 'ALUResult = ', hex(pipRegs['MEM/WB']['Read'].ALUResult), '\t', 'WriteRegNum = ', pipRegs['MEM/WB']['Read'].WriteRegNum

# @description Copy write to read
def Copy_write_to_read():
  global pipRegs

  pipRegs['IF/ID']['Read'] = copy.deepcopy(pipRegs['IF/ID']['Write'])
  pipRegs['ID/EX']['Read'] = copy.deepcopy(pipRegs['ID/EX']['Write'])
  pipRegs['EX/MEM']['Read'] = copy.deepcopy(pipRegs['EX/MEM']['Write'])
  pipRegs['MEM/WB']['Read'] = copy.deepcopy(pipRegs['MEM/WB']['Write'])

# @description Sign extend 16-bit offset to 32-bit
# @param {hex} offset
# @returns {string} offset
def sign_extend(offset):
  if offset >> 15 == 1:
    offset = hex(offset + 0xFFFF0000)
  else:
    offset = '0x' + hex(offset)[2:].zfill(8)
  return offset

# @description
# @param {string} offset
# @returns {hex} offset
def twos_complement(offset):
  hexOffset = int(offset, 16)
  if hexOffset >> 31 == 1:
    hexOffset -= math.pow(2, 32)
  return hexOffset

# Start program
if __name__ == '__main__':
  main()

# NOTE: CalcBTA and Zero were left out on purpose as they are not required
# in order to accomplish the tasks given by the test instructions