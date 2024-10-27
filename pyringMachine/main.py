#!/usr/bin/env python3
import sys
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
            print("Failed!")
            exit(0)
        else:
            c = s.cases[r]
            self.state = c.state
            self.tape[self.pos] = c.write
            self.pos += -1 if c.move=="L" else 1
            return c


script = open(sys.argv[1]).readlines()

t = TM(script, "aaa")

print(f"TuringMaschine t(\"{"".join(t.tape.values())}\");")
print("[1]")
while t.running():
    c = t.step()
    # print(t.state, c.write, t.pos)
    print(f"t.setTape(\"{c.write.replace("□", "")}\");")
    print(f"t.bez(\"position\", {t.pos}, 1, 10);")
print("t.wait(1); ")
