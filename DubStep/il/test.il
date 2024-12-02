
// Referenced Assemblies.
.assembly extern mscorlib
{
  .publickeytoken = (B7 7A 5C 56 19 34 E0 89 ) 
  .ver 4:0:0:0
}

// Our assembly.
.assembly test1
{
  .hash algorithm 0x00008004
  .ver 0:0:0:0
}

.module test.exe

// Definition of Program class.
.class private auto ansi beforefieldinit Program
  extends [mscorlib]System.Object
{
          
    .method private hidebysig static void Main(string[] args) cil managed
    {
    .locals (
       [0] int32 count,
       [1] int32 j,
       [2] float32 input,
       [3] int32 sum,
       [4] bool flag,
       [5] int32 _r5,
       [6] int32 _r6,
     )

   .entrypoint
   //.maxstack  8
     ldloca   sum
   ldc.r4   0
   stind.i4
   ldloc    count
   ldloca   j
   ldc.r4   1
   stind.i4
   ldloca   _r5
   ldc.r4   1
   stind.i4
m1:
   ldloca   _r6
   ldc.r4   0
   ldc.r4   1
   add
   stind.i4
   ldloc    _r5
   ldc.r4   0
   brfalse    m2
   ldloca   j
   ldloc    j
   ldloc    _r6
   add
   stind.i4
m2:
   ldloca   _r5
   ldc.r4   0
   stind.i4
   ldloc    j
   ldloc    count
   sub
   ldloc    _r6
   mul
   ldc.r4   0
   brfalse    m3
   ldloc    input
   ldloc    input
   call    void[mscorlib] System.Console::WriteLine(float32)
   ldloc    input
   ldc.r4   5
   brfalse    m4
   ldloca   sum
   ldloc    sum
   ldloc    input
   add
   stind.i4
   br     m5
m4:
   ldloca   sum
   ldloc    sum
   ldloc    input
   sub
   stind.i4
m5:
   br    m1
m3:
   ldloc    sum
   call    void[mscorlib] System.Console::WriteLine(int32)
   ret
}
}
