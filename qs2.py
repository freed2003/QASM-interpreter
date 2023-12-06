import argparse

class WeightedKet():

    def __init__(self, size) -> None:
        self.size = size
        self.amplitude = 1+0j
        self.ket = [0] * size

    def getket(self, i):
        return self.ket[i]
    
    def flip(self, i):
        # i = self.size -1 - i
        self.ket[i] = [1, 0][self.ket[i]]
    def getbin(self):
        return int("".join([str(i) for i in self.ket]), 2)
    def getstr(self):
        return "".join([str(i) for i in self.ket])
    def __str__(self) -> str:
        return "".join([str(i) for i in self.ket])
class Op():
    
    def __init__(self, type, op1, op2 = None) -> None:
        self.type = type
        self.op1 = op1
        self.op2 = op2
    

def simulate(instr):
    instr = instr.split("\n")
    qmap = {}
    qset = set()
    qsize = 0
    csize = 0
    ops = []
    state = {}
    for line in instr:
        if len(line) == 0:
            continue
        tokens = line.strip().split()
        if tokens[0] == "OPENQASM" or tokens[0] == "include":
            pass
        elif tokens[0] == "qreg":
            pass
        elif tokens[0] == "creg":
            csize = int(tokens[1][2:-2])
        elif tokens[0] == "h": 
            op1 = int(tokens[1][2:-2])
            qsize = max(qsize, op1 + 1)
            ops.append(Op("h", op1))
            qset.add(op1)
        elif tokens[0] == "x": 
            op1 = int(tokens[1][2:-2])
            qsize = max(qsize, op1 + 1)
            ops.append(Op("x", op1))
            qset.add(op1)
        elif tokens[0] == "t": 
            op1 = int(tokens[1][2:-2])
            qsize = max(qsize, op1 + 1)
            ops.append(Op("t", op1))
            qset.add(op1)
        elif tokens[0] == "tdg": 
            op1 = int(tokens[1][2:-2])
            qsize = max(qsize, op1 + 1)
            ops.append(Op("tdg", op1))
            qset.add(op1)
        elif tokens[0] == "cx": 
            s1, s2 = tokens[1].split(",")
            op1 = int(s1[2:-1])
            op2 = int(s2[2:-2])
            qsize = max(qsize, op1 + 1, op2 + 1)
            qset.add(op1)
            qset.add(op2)
            ops.append(Op("cx", op1, op2))
    start = 0
    qqmap = {}
    qsize = len(qset)
    for i in sorted(qset):
        qqmap[i] = start
        start += 1
    state["0"*qsize] = 1+0j
    # print(*state)
    for op in ops:
        newstate = {}
        for ket in state:
            if op.type == "h":
                if ket[qqmap[op.op1]] == "0":
                    newket = ket[:qqmap[op.op1]] + "1" + ket[qqmap[op.op1] + 1:]
                    newamp = state[ket] * ((1/2)**.5)
                    if ket in newstate:
                        newstate[ket] += newamp
                    else:
                        newstate[ket] = newamp
                    if newket in newstate:
                        newstate[newket] += newamp
                    else:
                        newstate[newket] = newamp
                else:
                    newket = ket[:qqmap[op.op1]] + "0" + ket[qqmap[op.op1] + 1:]
                    newamp = state[ket] * ((1/2)**.5)
                    if ket in newstate:
                        newstate[ket] += -newamp
                    else:
                        newstate[ket] = -newamp
                    if newket in newstate:
                        newstate[newket] += newamp
                    else:
                        newstate[newket] = newamp
            elif op.type == "x":
                newket = ket[:qqmap[op.op1]] + ["1", "0"][int(ket[qqmap[op.op1]])] + ket[qqmap[op.op1] + 1:]
                if newket in newstate:
                    newstate[newket] += state[ket]
                else:
                    newstate[newket] = state[ket]
            elif op.type == "t":
                if ket[qqmap[op.op1]] == "1":
                    newamp = ((1/2)**.5 + ((1/2)**.5)*1j) * state[ket]
                    if ket in newstate:
                        newstate[ket] += newamp
                    else:
                        newstate[ket] = newamp
                else:
                    if ket in newstate:
                        newstate[ket] += state[ket]
                    else:
                        newstate[ket] = state[ket]
            elif op.type == "tdg":
                if ket[qqmap[op.op1]] == "1":
                    newamp = ((1/2)**.5 - ((1/2)**.5)*1j) * state[ket]
                    if ket in newstate:
                        newstate[ket] += newamp
                    else:
                        newstate[ket] = newamp
                else:
                    if ket in newstate:
                        newstate[ket] += state[ket]
                    else:
                        newstate[ket] = state[ket]
            elif op.type == "cx":
                if ket[qqmap[op.op1]] == "1":
                    newket = newket = ket[:qqmap[op.op2]] + ["1", "0"][int(ket[qqmap[op.op2]])] + ket[qqmap[op.op2]+ 1:]
                else:
                    newket = ket
                if newket in newstate:
                    newstate[newket] += state[ket]
                else:
                    newstate[newket] = state[ket]

            
        # newstate = sorted(newstate,key = lambda x: x.bin())
        # print(nsd)
        state = newstate
    # statevec = [0] * (int(max(nsd.keys(), key=lambda x: int(x ,2)), 2) + 1)
    statevec = [0] * pow(2,qsize)
    for i in state:
        statevec[int(i, 2)] = round(state[i].real, 3) + round(state[i].imag, 3) * 1j
    # print(statevec)
    return statevec

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    file = parser.parse_args().file
    with open(file, "r") as f:
        code = f.read()
    simulate(code)
    