#!/usr/bin/env python3
import sys
import math

class Case:
    def __init__(self, w, m, e):
        self.write=w
        self.move=m
        self.state=e

class State:
    def __init__(self) -> None:
        self.cases = {}
    def addCase(self, e, cs):
        for c in cs:
            arr = c.split(":")
            r = arr[0]
            arr = arr[1].split(" ")
            w = arr[0]
            m = arr[1]
            # print("Case", r,w,e, m)
            self.cases[r] = Case(w,m,e)

class TM:
    def __init__(self, script, tape):
        self.tape = dict(enumerate(tape))
        self.pos = 0
        self.states = {}
        for line in script:
            line = line.strip()
            if not len(line):
                continue
            if line.startswith("{"):
                ss = [s.strip() for s in line[1:-1].split(",")]
                self.state = ss[0]
                self.endstates = ss[1:]
                continue

            s,e = line.split("->")
            s = s.strip()
            e,r = e.split("[")
            e = e.strip()
            r = r.split("\"")[1].split("\\n")

            if not s in self.states:
                self.states[s]=State()
            self.states[s].addCase(e, r)

        # for s, state in self.states.items():
        #     for r, c in state.cases.items():
        #         print(s, "->", c.state, r, c.write, c.move)
    def running(self):
        return self.state not in self.endstates

    def step(self):
        if self.pos in self.tape:
            r = self.tape[self.pos]
        else:
            r = "□"
        s = self.states[self.state]
        if not r in s.cases:
            return None
        else:
            c = s.cases[r]
            self.state = c.state
            if c.write == "□":
                if self.pos in self.tape:
                    del self.tape[self.pos]
            else:
                self.tape[self.pos] = c.write
            self.pos += -1 if c.move=="L" else 1
            return c

def outputAnim(t: TM, state=False, count =False):
    print(f"TuringMaschine t(\"{"".join(t.tape.values())}\", {t.pos}, 0, {-0.25 if state or count else 0});")
    if state:
        print(f"Text tState(\"z{t.state}\",0,0.72);")
    print("[1]")
    while t.running():
        c = t.step()
        if not c:
            print("t.addMark((255,0,0));")
            print("//Failed!")
            break
        # print(t.state, c.write, t.pos)
        print(f"t.setTape(\"{c.write.replace("□", "")}\");")
        if state:
            print(f"tState.setVar(\"text\",\"z{t.state}\");")
        print(f"t.bez(\"position\", {t.pos}, 1, 10);")
    else:
        print("t.addMark((0,255,0));")
    print("t.wait(1); ")

def outputConfigs(t: TM, latex: bool):
    def conf(t: TM):

        r = ""
        if not len(t.tape):
            start = t.pos
            end = t.pos
        else:
            start = min(*t.tape.keys(),t.pos)
            end = max(*t.tape.keys(), t.pos)
        for i in range(start,t.pos):
            if i in t.tape:
                c=t.tape[i]
            else:
                c="□"
            r+=c
        if latex:
            r+="z_{"+ t.state +"}"
        else:
            r+="(z"+ t.state + ")"
        for i in range(t.pos,end+1):
            if i in t.tape:
                c=t.tape[i]
            else:
                c="□"
            r+=c
        if latex:
            r=r.replace("□", "\\Box ")
        return r

    n=0
    out = f"\\underset{{ {n} }} {{ {conf(t)} }}" if latex else conf(t)
    while t.running():
        n+=1
        c = t.step()
        if not c:
            print(out)
            print("Failed!")
            return
        out+= f"\\vdash \\underset{{ {n} }} {{ {conf(t)} }}" if latex else  conf(t) + "\n "

    print(out)
    print("Done!")

def test(t: TM):
    while t.running():
        if not t.step():
            return False
    return True

script = open(sys.argv[1]).readlines()

t = TM(script, "")

# Testing

# c = 0
# tc = 1000
# for i in range(1, tc):
#     if math.log2(i)%1>0 and test(TM(script, "a"*i)):
#         print(i, "Broken")
#     else:
#         c+=1
# print("Successful: ", f"{c}/{tc-1}")

# Configurations

# outputConfigs(t, False)
outputConfigs(t, True)

# Animation
# outputAnim(t, state=True)
