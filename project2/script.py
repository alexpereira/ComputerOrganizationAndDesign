# @description Computer Architecture Project 2 - Cache Simulation
# @author Alex Pereira

# @description Main code 
def main():
  
  # Initialize main memory and cache
  mainMemory = initMem(2048, 255)
  cache = Cache(mainMemory, 16, 16)

  # Prompt command
  while 1:  
    cmd = raw_input("\n(R)ead, (W)rite, or (D)isplay Cache? ")
    address = None
    data = None

    if cmd.lower() == "q": break
    elif cmd.lower() == "r":
      address = raw_input("What address would you like to read? ")
      cache.read(address)
    elif cmd.lower() == "w":
      address = raw_input("What address would you like to write to? ")
      data = raw_input("What data would you like to write to at that address? ")
      cache.write(address, data)
    elif cmd.lower() == "d":
      cache.display()
    else: print "\nInvalid command: " + cmd + "\n"

# @description Initialize main memory
# @param {number} size
# @param {number} cap
# @returns {array} mem
def initMem(size, cap):
  mem = []

  for i in range(size):
    mem.append(i % (cap + 1))
  
  return mem

# @description Cache class
class Cache:
  def __init__(self, mainMemory, slotNumber, blockNumber):
    self.mem = mainMemory
    self.slots = []
    for number in range(slotNumber):
      self.slots.append(Slot(number, blockNumber))

  # @description Read data from address
  # @param {string} address
  def read(self, address):
    offset, begin, tag, slotNumber = self.decodeAddress(address)
    
    slot = self.slots[slotNumber]

    hit = slot.valid == 1 and slot.tag == tag
    miss = slot.valid != 1 or slot.tag != tag

    if hit:
      print "At that byte there is the value " + format(slot.data[offset], 'x') + " (Cache Hit)"
    
    if miss:
      # Update memory if slot is dirty
      if slot.dirty:
        writeBackBegin = int(format(slot.tag, 'x') + format(slot.number, 'x') + "0", 16)
        self.mem[writeBackBegin: writeBackBegin + 0x10] = slot.data

        # Update slot valid & dirty bit
        slot.valid = 0
        slot.dirty = 0

      # Update slot tag
      slot.tag = tag

      # Get data from memory
      slot.data = self.mem[begin: begin + 0x10]

      # Update slot valid bit
      slot.valid = 1
        
      print "At that byte there is the value " + format(slot.data[offset], 'x') + " (Cache Miss)"

  # @description Write data to address
  # @param {string} address
  # @param {string} data
  def write(self, address, data):
    offset, begin, tag, slotNumber = self.decodeAddress(address)
    
    slot = self.slots[slotNumber]

    hit = slot.valid == 1 and slot.tag == tag
    miss = slot.valid != 1 or slot.tag != tag

    if hit:
      # Update cache data
      slot.data[offset] = int(data, 16)

      # Update dity bit
      slot.dirty = 1

      print "Value " + data + " has been written to address " + address + " (Cache Hit)"
    
    if miss:
      # Update memory if slot is dirty
      if slot.dirty:
        writeBackBegin = int(format(slot.tag, 'x') + format(slot.number, 'x') + "0", 16)
        self.mem[writeBackBegin: writeBackBegin + 0x10] = slot.data

        # Update slot valid & dirty bit
        slot.valid = 0
        slot.dirty = 0

      # Update slot tag
      slot.tag = tag

      # Get data from memory
      slot.data = self.mem[begin: begin + 0x10]

      # Update cache data
      slot.data[offset] = int(data, 16)

      # Update slot valid & dirty bit
      slot.valid = 1
      slot.dirty = 1
      
      print "Value " + data + " has been written to address " + address + " (Cache Miss)"

  # @description Display current cache
  def display(self):
    print "\nSlot\tValid\tDirty\tTag\tData"
    for slot in self.slots:
      dataString = ""
      for data in slot.data:
        dataString += format(data, 'x').upper() + "\t" 
      
      print format(slot.number, 'x').upper() + "\t" + str(slot.valid) + "\t" + str(slot.dirty) + "\t" + format(slot.tag, 'x').upper() + "\t[" + dataString + "]"

  # @description Decode address
  # @param {string} address
  # @returns {number, number, number, number} offset, being, tag, slotNumber
  def decodeAddress(self, address):
    hexAddress = int(address, 16)
    offset = hexAddress & 0x000F
    begin = hexAddress & 0xFFF0
    tag = hexAddress >> 8
    slotNumber = (hexAddress & 0x00F0) >> 4

    return offset, begin, tag, slotNumber

# @description Slot class
class Slot:
  def __init__(self, number, blockNumber):
    self.number = number
    self.valid = 0
    self.dirty = 0
    self.tag = 0
    self.data = []

    for _ in range(blockNumber):
      self.data.append(0)

# Start program
if __name__ == '__main__':
  main()