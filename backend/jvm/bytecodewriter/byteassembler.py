"""
The Byteassembler takes a human-readable form of Bytecode and assembles it into actual bytecode.
opcodes.txt contains the list of opcodes and their arguments.
"""

import sys
import os.path
from backend.jvm.bytecodewriter.bytecompiler import MathHelper


def test():
    if not len(sys.argv) > 1:
        print("Please enter a file!")
        return

    if not (os.path.exists(sys.argv[1]) and os.path.isfile(sys.argv[1])):
        print("Not a file!")
        return

    f = open(sys.argv[1], "r")
    d = f.read()
    f.close()

    print(assemble(d).hex())


def assemble(code):
    a = Assembler()
    a.add_data(code)
    return a.assemble()


class Assembler:
    def __init__(self):
        self.data = ""
        self.labels = {}
        self.opcodes = {'aaload': (50, []), 'aastore': (83, []), 'aconst_null': (1, []), 'aload': (25, ['local']),
                        'aload_0': (42, []), 'aload_1': (43, []), 'aload_2': (44, []), 'aload_3': (45, []),
                        'anewarray': (189, ['const2']), 'areturn': (176, []), 'arraylength': (190, []),
                        'astore': (58, ['local']), 'astore_0': (75, []), 'astore_1': (76, []), 'astore_2': (77, []),
                        'astore_3': (78, []), 'athrow': (191, []), 'baload': (51, []), 'bastore': (84, []),
                        'bipush': (16, ['byte']), 'breakpoint': (202, []), 'caload': (52, []), 'castore': (85, []),
                        'checkcast': (192, ['const2']), 'd2f': (144, []), 'd2i': (142, []), 'd2l': (143, []),
                        'dadd': (99, []), 'daload': (49, []), 'dastore': (82, []), 'dcmpg': (152, []),
                        'dcmpl': (151, []), 'dconst_0': (14, []), 'dconst_1': (15, []), 'ddiv': (111, []),
                        'dload': (24, ['local']), 'dload_0': (38, []), 'dload_1': (39, []), 'dload_2': (40, []),
                        'dload_3': (41, []), 'dmul': (107, []), 'dneg': (119, []), 'drem': (115, []),
                        'dreturn': (175, []), 'dstore': (57, ['local']), 'dstore_0': (71, []), 'dstore_1': (72, []),
                        'dstore_2': (73, []), 'dstore_3': (74, []), 'dsub': (103, []), 'dup': (89, []),
                        'dup_x1': (90, []), 'dup_x2': (91, []), 'dup2': (92, []), 'dup2_x1': (93, []),
                        'dup2_x2': (94, []), 'f2d': (141, []), 'f2i': (139, []), 'f2l': (140, []), 'fadd': (98, []),
                        'faload': (48, []), 'fastore': (81, []), 'fcmpg': (150, []), 'fcmpl': (149, []),
                        'fconst_0': (11, []), 'fconst_1': (12, []), 'fconst_2': (13, []), 'fdiv': (110, []),
                        'fload': (23, ['local']), 'fload_0': (34, []), 'fload_1': (35, []), 'fload_2': (36, []),
                        'fload_3': (37, []), 'fmul': (106, []), 'fneg': (118, []), 'frem': (114, []),
                        'freturn': (174, []), 'fstore': (56, ['local']), 'fstore_0': (67, []), 'fstore_1': (68, []),
                        'fstore_2': (69, []), 'fstore_3': (70, []), 'fsub': (102, []), 'getfield': (180, ['const2']),
                        'getstatic': (178, ['const2']), 'goto': (167, ['tbranch']), 'goto_w': (200, ['fbranch']),
                        'i2b': (145, []), 'i2c': (146, []), 'i2d': (135, []), 'i2f': (134, []), 'i2l': (133, []),
                        'i2s': (147, []), 'iadd': (96, []), 'iaload': (46, []), 'iand': (126, []), 'iastore': (79, []),
                        'iconst_m1': (2, []), 'iconst_0': (3, []), 'iconst_1': (4, []), 'iconst_2': (5, []),
                        'iconst_3': (6, []), 'iconst_4': (7, []), 'iconst_5': (8, []), 'idiv': (108, []),
                        'if_acmpeq': (165, ['tbranch']), 'if_acmpne': (166, ['tbranch']),
                        'if_icmpeq': (159, ['tbranch']), 'if_icmpge': (162, ['tbranch']),
                        'if_icmpgt': (163, ['tbranch']), 'if_icmple': (164, ['tbranch']),
                        'if_icmplt': (161, ['tbranch']), 'if_icmpne': (160, ['tbranch']), 'ifeq': (153, ['tbranch']),
                        'ifge': (156, ['tbranch']), 'ifgt': (157, ['tbranch']), 'ifle': (158, ['tbranch']),
                        'iflt': (155, ['tbranch']), 'ifne': (154, ['tbranch']), 'ifnonnull': (199, ['tbranch']),
                        'ifnull': (198, ['tbranch']), 'iinc': (132, ['local', 'byte']), 'iload': (21, ['local']),
                        'iload_0': (26, []), 'iload_1': (27, []), 'iload_2': (28, []), 'iload_3': (29, []),
                        'impdep1': (254, []), 'impdep2': (255, []), 'imul': (104, []), 'ineg': (116, []),
                        'instanceof': (193, ['const2']), 'invokedynamic': (186, ['const2']),
                        'invokeinterface': (185, ['const2', 'byte']), 'invokespecial': (183, ['const2']),
                        'invokestatic': (184, ['const2']), 'invokevirtual': (182, ['const2']), 'ior': (128, []),
                        'irem': (112, []), 'ireturn': (172, []), 'ishl': (120, []), 'ishr': (122, []),
                        'istore': (54, ['local']), 'istore_0': (59, []), 'istore_1': (60, []), 'istore_2': (61, []),
                        'istore_3': (62, []), 'isub': (100, []), 'iushr': (124, []), 'ixor': (130, []),
                        'jsr': (168, ['tbranch']), 'jsr_w': (201, ['fbranch']), 'l2d': (138, []), 'l2f': (137, []),
                        'l2i': (136, []), 'ladd': (97, []), 'laload': (47, []), 'land': (127, []), 'lastore': (80, []),
                        'lcmp': (148, []), 'lconst_0': (9, []), 'lconst_1': (10, []), 'ldc': (18, ['const']),
                        'ldc_w': (19, ['const2']), 'ldc2_w': (20, ['const2']), 'ldiv': (109, []),
                        'lload': (22, ['local']), 'lload_0': (30, []), 'lload_1': (31, []), 'lload_2': (32, []),
                        'lload_3': (33, []), 'lmul': (105, []), 'lneg': (117, []), 'lookupswitch': (171, ['special']),
                        'lor': (129, []), 'lrem': (113, []), 'lreturn': (173, []), 'lshl': (121, []), 'lshr': (123, []),
                        'lstore': (55, ['local']), 'lstore_0': (63, []), 'lstore_1': (64, []), 'lstore_2': (65, []),
                        'lstore_3': (66, []), 'lsub': (101, []), 'lushr': (125, []), 'lxor': (131, []),
                        'monitorenter': (194, []), 'monitorexit': (195, []),
                        'multianewarray': (197, ['const2', 'byte']), 'new': (187, ['const2']),
                        'newarray': (188, ['atype']), 'nop': (0, []), 'pop': (87, []), 'pop2': (88, []),
                        'putfield': (181, ['const2']), 'putstatic': (179, ['const2']), 'ret': (169, ['local']),
                        'return': (177, []), 'saload': (53, []), 'sastore': (86, []), 'sipush': (17, ['short']),
                        'swap': (95, []), 'tableswitch': (170, ['special']), 'wide': (196, ['special'])}

    def add_data(self, data):
        self.data += data

    def assemble(self):
        code = b""

        self.data = self.data.split("\n")

        lb = dict()

        for ln, l in enumerate(self.data):
            l = self._remove_ws(l)

            if l == "":
                continue

            if l.endswith(":"):
                if l.count(" ") == 0:
                    l = l[:-1]

                    if l in self.labels:
                        print("The label '" + l + "' has already been defined.")
                        return

                    self.labels[l] = len(code)

                    if l in lb:
                        for e in lb[l]:
                            n = e[1]
                            x = e[0]

                            code = code[:x] + MathHelper.ifsign((len(code) - (x - 1)), n).to_bytes(n, "big") + code[
                                                                                                               x + n:]
                        del lb[l]
                    continue
                else:
                    print("Labels can't have spaces!")
                    return

            l = l.split(" ")

            op = self.opcodes[l[0]]
            code += op[0].to_bytes(1, "big")

            a = 1
            for x in op[1]:
                if x == "local":
                    code += int(l[a]).to_bytes(1, "big")
                elif x == "const2" or x == "const":
                    code += int(l[a]).to_bytes((1 if x == "const" else 2), "big")
                elif x == "byte":
                    n = 1
                    code += MathHelper.ifsign(int(l[a]), n).to_bytes(n, "big")
                elif x == "short":
                    n = 2
                    code += MathHelper.ifsign(int(l[a]), n).to_bytes(n, "big")
                elif x == "tbranch" or x == "fbranch":
                    n = (2 if x == "tbranch" else 4)

                    try:
                        code += MathHelper.ifsign(int(l[a]), n).to_bytes(n, "big")
                        continue
                    except ValueError:
                        pass

                    if not l[a] in self.labels:
                        code += bytes(n)

                        if l[a] in lb:
                            lb[l[a]] = [*lb[l[a]], (len(code) - n, n)]
                        else:
                            lb[l[a]] = [(len(code) - n, n)]
                        continue

                    f = self.labels[l[a]]
                    code += MathHelper.ifsign(-((len(code) - 1) - f), n).to_bytes(n, "big")
                elif x == "atype":
                    if l[a] == "boolean":
                        code += b"\x04"
                    elif l[a] == "char":
                        code += b"\x05"
                    elif l[a] == "float":
                        code += b"\x06"
                    elif l[a] == "double":
                        code += b"\x07"
                    elif l[a] == "byte":
                        code += b"\x08"
                    elif l[a] == "short":
                        code += b"\x09"
                    elif l[a] == "int":
                        code += b"\x0a"
                    elif l[a] == "long":
                        code += b"\x0b"
                    else:
                        print("Invalid array type!")
                        return
                elif x == "special":
                    print("Special cases aren't allowed yet.")
                    return
                a += 1

        for x in lb.keys():
            print("ERROR: Label '" + x + "' does not exist!")

        return code

    def _remove_ws(self, l):  # Remove whitespace
        i = 0
        for c in l:
            if c != " " and c != "\t":
                break
            else:
                i += 1
        return l[i:]


if __name__ == "__main__":
    test()
