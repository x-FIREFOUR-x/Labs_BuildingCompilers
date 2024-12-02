
convert_type = {"real": "float32", "int": "int32", "bool": "bool"}

class CLRM():             # CLR Machine
  def __init__(self):
    self.tableOfId    = {}
    self.codeIl   = []


  def saveCLICode(self, dir, fileName):
    fname = dir + fileName + ".il"
    f = open(fname, 'w')

    header = '''
// Referenced Assemblies.
.assembly extern mscorlib
{{
  .publickeytoken = (B7 7A 5C 56 19 34 E0 89 ) 
  .ver 4:0:0:0
}}

// Our assembly.
.assembly test1
{{
  .hash algorithm 0x00008004
  .ver 0:0:0:0
}}

.module {fileName}.exe

// Definition of Program class.
.class private auto ansi beforefieldinit Program
  extends [mscorlib]System.Object
{{
          
    .method private hidebysig static void Main(string[] args) cil managed
    {{
    .locals (
'''
    header = header.format(fileName=fileName)
    f.write(header)

    for var in self.tableOfId:
      indx, var_type, _ =  self.tableOfId[var]
      f.write(f"       [{indx - 1}] {convert_type[var_type]} {var},\n")
  
    str = '''     )

   .entrypoint
   //.maxstack  8
  '''
    
    f.write(str)

    codeil = ""
    for l in self.codeIl:
      if (len(l) == 3 and l[0] == 'm' and l[2] == ':'):
        codeil = codeil + l + "\n"
      else:
        codeil = codeil + "   " + l + "\n"
    f.write(codeil[:-1])


    end = '''
}
}
'''
    f.write(end)
