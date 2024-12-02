
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

.module test3.exe

// Definition of Program class.
.class private auto ansi beforefieldinit Program
  extends [mscorlib]System.Object
{
          
    .method public static void Main() cil managed {
    .locals (
       [0] int32 a,
       [1] float32 b
     )

    .entrypoint
    .maxstack  8
    ldloca   a
    ldc.i4   0
    stind.i4
    ldloca   b
    ldc.r4   3.1
    ldc.r4   2.0
    add
    stind.r4
    ldloc    b
    ldc.r4   5.0
    cgt
    brfalse    m1
    ldloc    a
    call    void[mscorlib] System.Console::WriteLine(int32)
    br     m2
m1:
    ldloc    b
    call    void[mscorlib] System.Console::WriteLine(float32)
m2:
    ret
}
}
