# Luraph v15.2 — dispatcher #14 opcode reference

Target: dispatcher #14 from the extracted VM chunk
`/tmp/main-luraph.bootstrap.chunk_249311_138937462.luau`.

The descriptions below are based on the handler bodies resolved by `vmmap.py`.
Names such as `v`, `S`, `i`, `M`, `n`, `U`, and `J` are VM internals:
- `v`: VM register table
- `J`: instruction pointer
- `S`: opcode array
- `i`, `M`, `n`, `U`, `L`, `r`: parallel operand/immediate arrays; the handler determines which role each field has
- `e`, `p`, `k`, `W`, `V`, `O`: auxiliary VM state/tables

This is an evolving reverse-engineering note, not a claim that every listed opcode occurs in the payload. The source-location group count is a structural property of the current VM source and may change as the resolver is corrected. It must not be confused with the number of opcode values used at runtime. The resolver and inventory generator walk past local setup statements and keep mixed mapped/unmapped groups unresolved. Regenerate the pending inventory after pulling the latest branch revision; do not reuse counts from older reports.

## Decoded opcodes

| Opcode | Handler / pseudocode | Interpretation | Confidence |
|---:|---|---|---|
| 0 | `v[n] = v[i] // v[M]` | Floor division of two registers. | High |
| 1 | `v[i] = v[M] % r` | Register modulo immediate. | High |
| 2 | `v[M] = p[i]` | Load from auxiliary lookup table `p` using immediate/index `i`. | High |
| 3 | `v[n] = i` | Store the operand-array table `i` itself in a VM register (not `i[J]`). | High |
| 4 | `v[n] = v[i] / L` | Register divided by immediate. | High |
| 5 | `J = (i <= v[M]) and J or n` | Conditional branch: keep the current PC when the comparison is true; otherwise jump to `n`. | High |
| 6 | `t({...}, 1, M, n, v)` | Copy the first `M` varargs into VM registers starting at `n`. | High |
| 7 | `v[i] = u(n, v[M])` | Bitwise AND of immediate `n` with register `v[M]`. | High |
| 8 | `v[i] = (v[n] == M)` | Equality comparison between a register and an immediate. | High |
| 9 | `V = v[M]` | Load a VM register into the interpreter's internal temporary `V`; not a register-to-register move. | High |
| 10 | `v[M][r] = i` | Write immediate `i` into table register `v[M]` at immediate key `r`. | High |
| 11 | `v[i] = v[n](v[M])` | Call function in `v[n]` with one register argument; store the first result in `v[i]`. | High |
| 12 | Saves/restores VM frame fields and sets `J = n`. | VM frame/context transition. The exact higher-level role is not yet established. | Medium |
| 13 | `v[i] = L * r` | Multiply two immediate operands and store the result. | High |
| 14 | `return v[i](Q(v, i+1, i+n))` | Tail-call function in `v[i]` with the argument range held in VM registers; return its results. | High |
| 15 | `v[n] = v[i] // M` | Floor division of register by immediate. | High |
| 16 | `J = (v[i] ~= L) and n or J` | Branch to `n` when register differs from immediate; otherwise keep the current PC. | High |
| 17 | `v[i] = W` | Copy internal temporary/state value `W` into a VM register. Its broader meaning is not yet known. | High for operation |
| 18 | `return v[n]()` | Tail-call function in `v[n]` with no arguments and return its results. Upvalues are closed before returning. | High |
| 19 | `v[M] = v[n][U]` | Read table field `U` from register-held table `v[n]`; store in `v[M]`. | High |
| 20 | `e[L] = r` | Write value `r` into auxiliary environment table `e` at key `L` (global/environment assignment). | High |
| 21 | `v[n](U)` | Call function in `v[n]` with immediate argument `U`; discard results. | High |
| 22 | `v[M] = v[i]` | Copy one VM register to another. | High |
| 23 | `v[n][v[M]] = U` | Write immediate `U` into table `v[n]`, using register `v[M]` as the key. | High |
| 24 | `J = v[n] and i or M` | Truthiness branch: jump to `i` if `v[n]` is truthy, otherwise to `M`. | High |
| 25 | `v[i]()` | Call function in `v[i]` without arguments; discard results. | High |
| 26 | Unpacks `M` encoded instruction words into `i`, `M`, `n`, and `S`; sets `S[J] = 57`. | Runtime instruction-stream expansion/decode. The current instruction becomes NOP after expansion. | High |
| 27 | `J = (v[M] < i) and J or n` | Keep the current PC when `v[M] < i`; otherwise branch to `n` (equivalent to taking the branch when `v[M] >= i`). | High |
| 28 | `v[i] = v[M] % v[n]` | Remainder of two VM register values. | High |
| 29 | `e[U][r] = L` | Write immediate value `L` into nested auxiliary table `e[U]` at immediate key `r`. This has the shape of an environment-table write, but the broader role of `e` is inferred from neighboring handlers. | High for the write; Medium for the role of `e` |
| 30 | Multi-slot sequence: load receiver `R = v[n[J]]`, place receiver/method in `v[h+1]` and `v[h] = R[U[J]]`, and apply the next three instruction slots as register setup. At `J+4`, `h=M[J+4]`, argument count `argc=i[J+4]`, result count `nres=n[J+4]`; call `v[h]` with registers `h+1..h+argc`, copy `nres` returned values into registers starting at `h`, then `J += 4`. | Fused table-method lookup + argument setup + multi-result call. It consumes five instruction slots (`J` through `J+4`); retain this as a compound handler, not a simple single-op call. | High for the observed effects; Medium for the higher-level mnemonic |
| 31 | `v[M] = v[i] * n` | Multiply register `v[i]` by immediate `n` and store in `v[M]`. | High |
| 32 | `J = (v[i] < v[M]) and J or n` | Keep the current PC when `v[i] < v[M]`; otherwise branch to `n` (branch condition `v[i] >= v[M]`). | High |
| 33 | `v[n] = n` | Store the entire operand-array table `n` in register `v[n[J]]`; this is not the scalar operand `n[J]`. | High |
| 34 | `v[i] = -v[M]` | Unary numeric negation of register `v[M]`. | High |
| 35 | Close the tracked open-upvalue cell associated with register index `i[J]`; save its current value from `v[i[J]]` and remove the entry from the open-upvalue map `a`. | Close one open upvalue for a VM register. | High for the state transition |
| 36 | `v[i] = e[L]` | Load an entry from the environment table `e` at immediate key `L` into `v[i]`. | High |
| 37 | `v[i](Q(v[n], 1, v[n].n))` | Call the function in `v[i]` with all values in the packed argument list held in `v[n]`; discard the call's results. | High for the call shape |
| 38 | Close all tracked open upvalues in `a`; snapshot each pending register range/capture tracked in `B` into a fresh table and update its cell; then `return U`. | VM return with upvalue/capture cleanup and one explicit return value `U[J]`. The exact higher-level meaning of `B` remains provisional. | High for the observed effects; Medium for `B`'s role |
| 39 | `J = (U < v[n]) and J or M` | Keep the current PC when immediate `U` is less than `v[n]`; otherwise branch to `M` (branch condition `U >= v[n]`). | High |
| 40 | `v[M] = (n * U) mod 2^32` | Low 32 bits of multiplication of the two immediate operands `n` and `U`. | High |
| 41 | Builds a capture list from triples in descriptor `r`: type 0 reads `v[hy]`, type 1 reuses/creates an entry in the open-upvalue map `a`, type 2 reuses/creates an entry in the secondary map `B` (carrying the descriptor's extra field), and type 3 reads `k[hy]`; passes the assembled list to the callable in `r[J]` and stores its result in `v[M[J]]`. | Closure/prototype construction with explicit capture descriptors. The exact VM-level names for capture types 1 and 2 remain provisional. | High for descriptor handling and call/result; Medium for the precise capture-type semantics |
| 42 | Close all tracked open upvalues in `a`, snapshot the pending register ranges/captures tracked in `B`, then `return`. | VM return with cleanup and no explicit return value. The exact higher-level meaning of `B` remains provisional. | High for the observed effects; Medium for `B`'s role |
| 43 | `v[M] = A(v[n], U)` | Apply helper `A` to register `v[n]` and immediate `U`; store its result in `v[M]`. The operator/semantic meaning of `A` is not established from this handler alone. | High for data flow; Unknown for helper meaning |
| 44 | For each of the three register indices `M[J]`, `i[J]`, and `n[J]`, close the corresponding tracked open-upvalue cell in `a` and save its current register value. | Close upvalues associated with three VM register slots. | High for the state transition |
| 45 | `v[M] = #v[n]` | Apply the length operator to the value in register `v[n]` and store the result in `v[M]`. | High |
| 46 | `v[M] = n * v[i]` | Multiply immediate `n` by register `v[i]` and store the result in `v[M]`. | High |
| 47 | `v[M] = (i * v[n]) mod 2^32` | Low 32 bits of immediate × register multiplication. | High |
| 48 | `v[M] = v[n] - v[i]` | Register subtraction. | High |
| 49 | `v[M] = v[i][n]` | Read key `n` from table/value in register `v[i]` and store the result in `v[M]`. | High |
| 50 | `v[i] = e[r][L]` | Read `e[r][L]` from the nested environment table and store it in `v[i]`. | High for the access |
| 51 | `v[M], v[M+1] = i, r` | Load two immediate operands into consecutive VM registers starting at `M`. | High |
| 52 | `q, I, w, G = O[5], O[7], O[6], O[9]; O = O[8]` | Restore interpreter state fields from the saved frame and pop the frame chain. | High for the state restoration; Medium for frame naming |
| 53 | `v[M] = _(v[M](Q(v, M+1, M+i)))` | Call the function in register `M` with `i` arguments from the following registers and store the first return value back in `v[M]`. | High |
| 54 | `v[M] = u(v[n], U)` | Bitwise AND of register `v[n]` with immediate operand `U` (same normalization/bitwise helper as opcode 7). | High, based on the established helper use |
| 55 | `v[M] = _(v[n](v[i]))` | Call the function in `v[n]` with one argument from `v[i]`; pass the call result through helper `_` and store that helper's result in `v[M]`. The exact transformation performed by `_` is not inferred from this line alone. | High for call/argument/data flow; unresolved for `_` |
| 56 | `v[n] = (v[i] * v[M]) mod 2^32` | Low 32 bits of register × register multiplication. | High |
| 57 | No operation. | NOP. | High |
| 58 | `J = v[n]` | Unconditional jump to the address held in a register. | High |
| 59 | `v[M][r] = U` | Write immediate `U` into the table held in register `v[M]`, using immediate key `r`. | High |
| 60 | `h = k[i]; h[5][h[4]][v[M]] = v[n]` | Resolve the captured/upvalue cell referenced by `k[i]`, then write `v[n]` into the table held by that captured value at key `v[M]`. This mutates the referenced table; it does not replace the upvalue cell itself. | High for the dereference and write |
| 61 | Close tracked open upvalues in `a`, snapshot pending captured register ranges in `B`, then `return v[i]`. | VM return of the value in register `v[i]`, preceded by upvalue/capture cleanup. The precise abstraction represented by `B` remains provisional. | High for the return and cleanup effects |
| 62 | `v[M] = i` | Load immediate into a VM register. | High |
| 63 | `v[M] = A(U, v[n])` | Call helper `A` with immediate `U` and register value `v[n]`; store its result in `v[M]`. The helper's semantic operation is not established by this handler alone. | High for data flow; unresolved for `A` |
| 64 | `W = v[i]` | Copy register `v[i]` into the interpreter-local temporary/state variable `W`; this does not write to a VM register. | High |
| 65 | `my = M; J = n + 1; break` | Store operand `M` in interpreter-local `my`, set the next PC to `n+1`, and exit the current enclosing loop. The broader meaning of `my` depends on the loop's caller/context. | High for the visible effects; Medium for the higher-level purpose |
| 66 | `J = (v[i] < L) and J or n` | Keep the current PC when `v[i] < L`; otherwise branch to `n` (branch condition `v[i] >= L`). | High |
| 67 | `v[n] = (v[M] ~= U)` | Compare register `v[M]` with immediate `U` for inequality; store the boolean in `v[n]`. | High |
| 68 | `v[M] = _(v[i]())` | Call the function in `v[i]` with no arguments; pass the call result through helper `_` and store that helper's result in `v[M]`. The exact transformation performed by `_` is not inferred from this line alone. | High for call/data flow; unresolved for `_` |
| 69 | Close tracked open upvalues in `a`, snapshot pending captured register ranges in `B`, then `return L, r`. | VM return of the two immediate values `L[J]` and `r[J]`, preceded by upvalue/capture cleanup. The precise abstraction represented by `B` remains provisional. | High for the return and cleanup effects |
| 70 | Loads `H`, `S`, `n`, and `i` into four consecutive registers starting at `n[J]`; advances `J` by 3. | Special VM environment/helper setup instruction. | High |
| 71 | `v[M] = r .. v[i]` | Concatenate immediate operand `r` on the left with register value `v[i]` on the right; store the result in `v[M]`. | High |
| 72 | `v[n] = v[M] + i` | Add immediate operand `i` to register `v[M]`; store the result in `v[n]`. | High |
| 73 | Save the current frame in `O`; create `R = K(b)`; call `R(p, v[h], v[h+1], v[h+2])`; then set `G=n`, `J=M`, and `q=R`. | Frame/context transition involving helper-created callable `R`; saves prior interpreter state, invokes the new callable with `p` and three register values, then switches interpreter state fields. The exact role of `K(b)` and the new context is not established here. | High for the visible sequence; Medium for the semantic label |
| 74 | `J = (v[M] ~= i) and n or J` | Branch to `n` when register `v[M]` differs from immediate `i`; otherwise keep the current PC. | High |
| 75 | Reads and advances through an encoded byte buffer in `H[4]`/`H[7]`, decodes a length/value, applies helper-based byte transformations to the selected range, then sets `i[J]=38`, `M[J]=138`, `n[J]=232`, and `S[J]=57`. | In-place byte-buffer transform/decode followed by rewriting the current instruction slot to opcode 57 (NOP) with replacement operands. Do not label the transform as a specific cipher without resolving helpers `j`, `D`, `x`, `Y`, and `P`. | High for buffer mutation and instruction rewrite; unresolved for transform algorithm |
| 76 | `v[i] = (v[M] >= n)` | Compare register `v[M]` against immediate `n` using greater-than-or-equal; store the boolean in `v[i]`. | High |
| 77 | `J = (v[n] <= i) and J or M` | Keep the current PC when `v[n] <= i`; otherwise branch to `M` (branch condition `v[n] > i`). | High |
| 78 | `v[h], v[h+1] = v[i], n` where `h=M` | Copy register `v[i]` into register `M`, and immediate `n` into the next register `M+1`. | High |
| 79 | `v[i] = floor(v[n] % 2^32)` (NaN maps to 0) | Normalize the numeric value in `v[n]` to an integer in the unsigned 32-bit range and store it in `v[i]`. | High |
| 80 | Build a packed argument list from VM registers `h+1..h+R-1` plus the extra packed table in `v[h+R]`; call `v[h]` with the combined arguments; copy `d` results back into VM registers starting at `h`. | Variable-argument/multi-return call instruction. The helper `_` packages call results and `t` copies the requested return count; do not reduce this to a single-return call. | High for argument/result flow |
| 81 | `v[M], v[M+1] = v[i], r` | Copy register `v[i]` into register `M` and immediate operand `r` into the following register `M+1`. | High |
| 82 | `v[i][L] = v[n]` | Write register value `v[n]` into the table held in register `v[i]`, using immediate key `L`. | High |
| 83 | `v[M] = n - v[i]` | Subtract register value `v[i]` from immediate operand `n`; store the result in `v[M]`. Operand order matters. | High |
| 84 | `v[i] = k[n][v[M]]` | Read key `v[M]` from auxiliary table/object `k[n]` and store the result in `v[i]`. The handler establishes the lookup but not the higher-level role of `k`. | High for data flow; unresolved for the role of `k` |
| 85 | `v[i] = v[M] - n` | Subtract immediate operand `n` from register `v[M]`; store the result in `v[i]`. | High |
| 86 | `v[n] = _(v[i](Q(v[M], 1, v[M].n)))` | Call function `v[i]` with the argument sequence extracted from packed argument table `v[M]` (using its `.n` count); pass the call result through helper `_` and store it in `v[n]`. The exact result-packing behavior of `_` is unresolved. | High for call/argument flow; unresolved for `_` |
| 87 | Close tracked open upvalues in `a`, snapshot/copy pending captured register ranges tracked in `B`, then `return v[i](v[n], v[M])`. | Tail-call function `v[i]` with two register arguments (`v[n]`, `v[M]`) and return its results after upvalue/capture cleanup. The precise abstraction represented by `B` remains provisional. | High for call and cleanup effects |
| 88 | `v[i] = (L * v[n]) mod 2^32` | Multiply immediate `L` by register `v[n]`, retaining the low 32 bits. The handler implements the product using 16-bit halves and helper shifts/combinations. | High |
| 89 | `v[i][v[n]] = v[M]` | Write register value `v[M]` into the table held in `v[i]`, using register `v[n]` as the key. | High |
| 90 | `v[n] = (v[M] > v[i])` | Compare two VM registers using greater-than and store the boolean result in `v[n]`. | High |
| 91 | `v[M] = n ^ v[i]` | Raise immediate base `n` to the power held in register `v[i]`; store the result in `v[M]`. In Luau, `^` is exponentiation, not bitwise XOR. | High |
| 92 | `J = (v[i] <= r) and J or M` | Keep the current PC when `v[i] <= r`; otherwise branch to immediate target `M` (branch condition `v[i] > r`). | High |
| 93 | `J = v[M]` | Unconditional jump to the address held in register `v[M]`. | High |
| 94 | `v[M] = A(v[n], i)` | Call helper `A` with register value `v[n]` and immediate operand `i`; store its result in `v[M]`. The semantic operation performed by `A` is not established by this handler alone. | High for data flow; unresolved for `A` |
| 95 | `J = v[M] and i or n` | Truthiness branch based on register `v[M]`. | High |
| 96 | `for x = M, i do v[x] = nil end` | Clear every VM register in the inclusive range from `M[J]` through `i[J]` (the loop performs no writes if the start exceeds the end). | High |
| 97 | `h = i; v[h], v[h+1] = M, v[n]` | Load immediate operand `M` into register `i`, and copy register `v[n]` into the following register `i+1`. | High |
| 98 | `v[i] = (v[M] == r)` | Compare register `v[M]` with immediate operand `r`; store the boolean equality result in `v[i]`. | High |
| 99 | `v[M], v[M+1] = v[n], v[i]` | Copy two registers into consecutive destination registers (parallel assignment; not a swap). | High |
| 100 | `v[M] = v[n] / v[i]` | Divide register `v[n]` by register `v[i]`; store the result in `v[M]`. | High |
| 101 | `v[n] = (v[i] < M)` | Compare register `v[i]` with immediate operand `M`; store the boolean less-than result in `v[n]`. | High |
| 102 | Reads/advances an encoded byte buffer in `H[4]`/`H[7]`, decodes a variable-length span, transforms the corresponding bytes in place using helpers `j`, `D`, `x`, `Y`, and `P`, then sets `i[J]=235`, `M[J]=80`, `n[J]=145`, and `S[J]=57`. | In-place byte-buffer decode/transform followed by rewriting the current instruction slot to opcode 57 (NOP) with replacement operands. The exact transformation algorithm is unresolved; do not assign it a cipher name without resolving the helpers. | High for buffer mutation and instruction rewrite; unresolved for algorithm |
| 103 | `h = i; local ok, value = q(); if ok then v[h] = value; J = n else J = M end; R, d = ok, value` | Call helper `q()` and branch on its first result. If truthy, store the second result in register `i` and jump to `n`; otherwise jump to `M`. Also copy the returned pair into interpreter state `R,d`. The higher-level purpose of `q()` is not established here. | High for control/data flow; unresolved for `q`'s role |
| 104 | `v[M] = v[i]()` | Call function in `v[i]` without arguments; store the first return value in `v[M]`. | High |
| 105 | `J = (L ~= v[n]) and i or J` | Branch to immediate target `i` when register `v[n]` differs from immediate `L`; otherwise keep the current PC. | High |
| 106 | `v[M](v[n])` | Call function in `v[M]` with one register argument; discard results. | High |
| 107 | `v[n] = (v[M] < v[i])` | Compare registers `v[M]` and `v[i]` using less-than; store the boolean result in `v[n]`. | High |
| 108 | `h = k[n]; h[5][h[4]] = L` | Resolve the capture/upvalue cell referenced by `k[n]` and assign immediate value `L` to that cell's stored value. This is a write to the captured variable itself, unlike opcode 60 which indexes into a table held by the captured value. | High for the observed dereference/write; Medium for the upvalue label |
| 109 | `v[n] = l(v[M])` | Apply helper `l` to register value `v[M]` and store the result in `v[n]`. The meaning of `l` is unresolved from this handler alone. | High for data flow; unresolved for `l` |
| 110 | `J = (i < v[M]) and J or n` | Keep the current PC when immediate `i` is less than register `v[M]`; otherwise branch to `n` (branch condition `i >= v[M]`). | High |
| 111 | `v[i] = v[n] ^ M` | Raise register value `v[n]` to immediate exponent `M`; store the result in `v[i]`. In Luau, `^` is exponentiation, not bitwise XOR. | High |
| 112 | `v[M], v[i] = v[n]()` | Call function in register `v[n]` with no arguments and assign its first two return values to registers `M` and `i`, respectively. | High |
| 113 | `v[M] = X(v[n], i)` | Apply helper `X` to register value `v[n]` and immediate operand `i`; store the result in `v[M]`. The helper's exact operation is unresolved from this handler alone. | High for data flow; unresolved for `X` |
| 114 | `v[n](v[M], Q(v[i], 1, v[i].n))` | Call function in `v[n]` with register `v[M]` as the first argument, followed by all arguments unpacked from the packed table in `v[i]`; discard the call's results. | High |
| 115 | Reads/advances the encoded byte buffer in `H[4]`/`H[7]`, decodes a variable-length span, applies helper-based byte transformations to the selected range, then sets `i[J]=86`, `M[J]=11`, `n[J]=191`, and `S[J]=57`. | In-place byte-buffer transform/decode followed by rewriting the current instruction slot to opcode 57 (NOP) with replacement operands. The precise algorithm remains unknown because helpers `j`, `D`, `x`, `Y`, and `P` have not been resolved. | High for mutation and instruction rewrite; unresolved for algorithm |
| 116 | Close tracked open upvalues in `a`, snapshot/copy pending captured register ranges tracked in `B`, then `return v[M[J]], Q(v[i[J]], 1, v[i[J]].n)`. | Return the value in register `v[M]` followed by all values in the packed list held in `v[i]`, after upvalue/capture cleanup. The final `Q(...)` expression expands to multiple return values. | High |
| 117 | `v[n] = not v[M]` | Apply logical NOT to register `v[M]` and store the boolean result in `v[n]`. | High |
| 118 | `F = _(v[h](Q(v, h+1, h+R))); t(F, 1, d, h, v)` where `h=M`, `R=i`, `d=n` | Call function in register `h` with the next `R` registers as arguments, package its results through helper `_`, and copy `d` results back into registers starting at `h`. This is a variable-argument, fixed-result-count call. | High for argument/result flow; unresolved only for `_` packaging details |
| 119 | `v[M] = (v[i] < r)` | Compare register `v[i]` with immediate operand `r` using less-than; store the boolean result in `v[M]`. | High |
| 120 | `v[i] = (v[M] ~= n)` | Compare register `v[M]` with immediate operand `n` for inequality; store the boolean result in `v[i]`. | High |
| 121 | `v[M] = j(r, v[i])` | Apply helper `j` to immediate operand `r` and register value `v[i]`; store its result in `v[M]`. The helper's exact operation is unresolved. | High for data flow; unresolved for `j` |
| 122 | Close tracked open upvalues in `a`, snapshot/copy pending captured register ranges tracked in `B`, then `return U, v[M]`. | Return immediate value `U[J]` followed by register value `v[M[J]]`, after upvalue/capture cleanup. | High |
| 123 | `local ok, a, b = q(); if ok then v[i], v[i+1] = a, b; J=n else J=M end; R,d,z=ok,a,b` | Call helper `q()` for a three-value result. If the first value is truthy, store the next two values in consecutive registers beginning at `i` and jump to `n`; otherwise jump to `M`. Also preserve the returned triple in interpreter state `R,d,z`. | High for control/data flow; unresolved for `q`'s role |
| 124 | Derives a rolling decode value `R` from `M[J]` and state `W`, splits the packed value into 7-bit fields, merges those fields into `S[J]`, `n[J]`, `i[J]`, and `M[J]`, then decrements `J`. | Decode/rewrite the current instruction's opcode and three operands using state-dependent bit fields; `J=J-1` causes the rewritten instruction slot to be processed again by the dispatch loop. Helpers `j`, `u`, `C`, and `X` remain unresolved, so this is a structural description rather than a named cipher/encoding. | High for instruction-field rewrite; medium for the precise decode interpretation |
| 125 | `J = (v[i] ~= v[M]) and n or J` | Branch to immediate target `n` when registers `v[i]` and `v[M]` differ; otherwise keep the current PC. | High |
| 126 | `v[M] = A(i, v[n])` | Call helper `A` with immediate operand `i` and register value `v[n]`; store the result in `v[M]`. The semantic operation performed by `A` is unresolved. | High for data flow; unresolved for `A` |
| 127 | `v[i] = v[n] * v[M]` | Multiply register values `v[n]` and `v[M]` and store the ordinary numeric product in `v[i]`. Unlike opcodes 56 and 134, this handler does not explicitly reduce the product modulo 2^32. | High |
| 128 | Close tracked open upvalues in `a`, snapshot/copy pending captured register ranges tracked in `B`, then `return v[M](v[n])`. | Tail-call function in register `v[M]` with one register argument `v[n]` and return all results, after upvalue/capture cleanup. | High |
| 129 | Close tracked open upvalues in `a`, snapshot/copy pending captured register ranges tracked in `B`, then `return v[i](r, L)`. | Tail-call function in register `v[i]` with two immediate arguments `r[J]` and `L[J]`, returning all results after upvalue/capture cleanup. | High |
| 130 | `v[M] = j(U, r)` | Apply helper `j` to the two immediate operands `U` and `r`; store its result in `v[M]`. The helper's exact operation is unresolved. | High for data flow; unresolved for `j` |
| 131 | `v[i] = M` | Store the entire operand-array table `M` itself in VM register `v[i[J]]`, not the scalar operand `M[J]`. | High |
| 132 | Seed rolling state `R` from `M[J]` and `W`; for each of the next `n[J]` instruction slots, update `R` with helper-based recurrence and merge 7-bit fields from `R` into `i[h]`, `M[h]`, `n[h]`, and `S[h]`; finally set `S[J]=57`. | Decode/rewrite a run of following instruction records using a rolling state derived from `W`; the current decoder instruction becomes NOP after expansion. The exact bitwise recurrence is not named because helpers `j`, `u`, `C`, and `X` remain unresolved. | High for loop bounds, state flow and instruction-array writes; unresolved for recurrence semantics |
| 133 | `h=M; v[h], v[h+1] = i, n` | Load two immediate operands `i[J]` and `n[J]` into consecutive VM registers starting at `M[J]`. | High |
| 134 | `v[i] = (v[n] * v[M]) mod 2^32` | Multiply register values `v[n]` and `v[M]`, retaining the low 32 bits, then store in `v[i]`. The handler implements the product using 16-bit halves. | High |
| 135 | `v[i] = v[n] .. v[M]` | Concatenate register values `v[n]` and `v[M]` in that order; store the result in `v[i]`. | High |
| 136 | `J = M` | Unconditional jump to immediate target. | High |
| 137 | `h=k[M]; v[n] = h[5][h[4]]` | Resolve the captured/upvalue cell referenced by `k[M]` and load its current value into register `v[n]`. This is the read counterpart to the captured-cell write in opcode 108. | High for the dereference and load; Medium for the upvalue label |
| 138 | `k[i][r] = M` | Write immediate value `M[J]` into auxiliary table `k[i[J]]` at immediate key `r[J]`. The precise higher-level role of this `k` entry is not established by this handler alone. | High for the write; unresolved for the role of `k` |
| 139 | `v[i] = (r * L) mod 2^32` | Multiply the two immediate operands `r[J]` and `L[J]`, retaining the low 32 bits; store the result in register `v[i[J]]`. The handler computes the product using 16-bit halves. | High |
| 140 | `v[i] = k[n]` | Load entry `k[n[J]]` from auxiliary table `k` into register `v[i[J]]`. This is a direct table lookup, not a dereference through a captured-cell record. | High for data flow; unresolved for the role of `k` |
| 141 | `h=k[M]; v[n] = h[5][h[4]][v[i]]` | Resolve the captured/upvalue cell referenced by `k[M[J]]`, then use the value stored in that cell as a table and read its field indexed by register `v[i[J]]`; store the field in `v[n[J]]`. | High for dereference and table read; Medium for upvalue terminology |
| 142 | `v[i] = r - v[M]` | Subtract register value `v[M[J]]` from immediate operand `r[J]`; store the result in `v[i[J]]`. Operand order is immediate minus register. | High |
| 143 | `v[i], v[i+1] = r, M` | Load immediate operands `r[J]` and `M[J]` into two consecutive VM registers starting at `i[J]`. | High |
| 144 | `v[n][M] = i` | Write immediate operand `i[J]` into the table held in register `v[n[J]]`, using immediate key `M[J]`. | High |
| 145 | `v[n] = S` | Store the entire opcode array `S` itself in register `v[n[J]]`, not the scalar opcode `S[J]`. | High |
| 146 | `v[M] = u(v[n], v[i])` | Apply helper `u` to the two register values `v[n[J]]` and `v[i[J]]`; based on opcode 7 and 54, this helper performs bitwise AND. | High |
| 147 | `h=k[n]; h[5][h[4]][L] = U` | Resolve the captured/upvalue cell referenced by `k[n[J]]`, then write immediate `U[J]` into the table held by that captured value at immediate key `L[J]`. This mutates the captured table, not the captured cell's value. | High for dereference and write; Medium for upvalue terminology |
| 148 | `v[i] = (v[n] ~= v[M])` | Compare registers `v[n[J]]` and `v[M[J]]` for inequality; store the boolean result in `v[i[J]]`. | High |
| 149 | `v[i] = (v[n] <= L)` | Compare register `v[n[J]]` with immediate operand `L[J]` using less-than-or-equal; store the boolean result in `v[i[J]]`. | High |
| 150 | `v[M][n] = v[i]` | Write register value `v[i[J]]` into the table held in register `v[M[J]]`, using immediate key `n[J]`. | High |
| 151 | `h=n; R={...}; d=M; t(R,1,h-1,d,v); v[d+h-1]=_(py(h,...))` | Build a variable-argument call/packing frame: copy `h-1` values from VM registers beginning at `d` into the front of the vararg list `R`, then invoke helper `py` with count `h` and the incoming varargs; pass the result through `_` and store it in register `d+h-1`. The exact contracts of `py` and `_` are unresolved, so the handler is best described as vararg prefix assembly plus helper invocation. | High for register/vararg data flow; unresolved for `py` and `_` |
| 152 | `v[n] = v[M] ^ U` | Raise register value `v[M[J]]` to immediate exponent `U[J]`; store the result in `v[n[J]]`. In Luau, `^` denotes exponentiation, not XOR. | High |
| 153 | `v[M] = j(v[n], v[i])` | Apply helper `j` to register values `v[n[J]]` and `v[i[J]]`; store its result in `v[M[J]]`. The helper's exact operation is unresolved from this handler alone. | High for data flow; unresolved for `j` |
| 154 | `v[M] = v[i] - r` | Subtract immediate operand `r[J]` from register value `v[i[J]]`; store the result in `v[M[J]]`. | High |
| 155 | `v[M] = v[n] * U` | Multiply register value `v[n[J]]` by immediate operand `U[J]`; store the ordinary numeric product in `v[M[J]]`. No explicit modulo-2^32 reduction appears in this handler. | High |
| 156 | `v[i] = A(v[n], v[M])` | Apply helper `A` to register values `v[n[J]]` and `v[M[J]]`; store the result in `v[i[J]]`. Its semantic operation is not established from this handler alone. | High for data flow; unresolved for `A` |
| 157 | `v[n] = v[M] + v[i]` | Add register values `v[M[J]]` and `v[i[J]]`; store the result in `v[n[J]]`. | High |
| 158 | Close tracked open upvalues in `a`, snapshot/copy pending captured register ranges tracked in `B`, then `return v[M[J]], v[i[J]]`. | Return two VM register values, in order `v[M]` then `v[i]`, after upvalue/capture cleanup. | High |
| 159 | Derive rolling decode state `R` from `M[J]` and `V`; split packed operand `n[J]` into variable-width 7/14/21-bit fields; merge those fields plus state-derived 7-bit chunks into `i[J]`, `n[J]`, `M[J]`, and `S[J]`; finally decrement `J`. | Decode/rewrite the current instruction's opcode and three operands using a state-dependent packed representation. Decrementing `J` causes the rewritten slot to be dispatched again. Helpers `j`, `u`, `C`, and `X` remain unresolved, so this is a structural description rather than a named encoding algorithm. | High for field extraction/rewrite; medium for the precise decode interpretation |
| 160 | `v[M], v[M+1] = U, v[n]` | Load immediate operand `U[J]` into register `M[J]`, and copy register `v[n[J]]` into the following register `M+1`. | High |
| 161 | `v[M] = (v[n] <= v[i])` | Compare registers `v[n[J]]` and `v[i[J]]` using less-than-or-equal; store the boolean result in `v[M[J]]`. | High |
| 162 | `v[n] = k[M][U]` | Read immediate key `U[J]` from auxiliary table `k[M[J]]`; store the value in register `v[n[J]]`. | High for data flow; unresolved for the role of `k` |
| 163 | `v[i] = r` | Load immediate operand `r[J]` into register `v[i[J]]`. | High |
| 164 | `v[i] = C(v[M], n)` | Apply helper `C` to register value `v[M[J]]` and operand `n[J]`; store the result in `v[i[J]]`. In the decoder's other arithmetic, `C` is used to extract higher-order bit fields, but its exact general contract is not inferred from this handler alone. | High for data flow; provisional for helper meaning |
| 165 | `v[M](U, r)` | Call function in register `v[M[J]]` with two immediate arguments, `U[J]` and `r[J]`; discard all return values. | High |
| 166 | `v[n] = j(v[M], i)` | Apply helper `j` to register value `v[M[J]]` and immediate operand `i[J]`; store the result in `v[n[J]]`. The helper's exact operation is unresolved from this handler alone. | High for data flow; unresolved for `j` |
| 167 | `k[M][r] = v[i]` | Write register value `v[i[J]]` into auxiliary table `k[M[J]]` at immediate key `r[J]`. | High for the write; unresolved for the role of `k` |
| 168 | `v[i] = v[n][v[M]]` | Read key `v[M[J]]` from the value in register `v[n[J]]`; store the result in `v[i[J]]`. | High |
| 169 | Close tracked open upvalues in `a`, snapshot/copy pending captured register ranges in `B`, then `return v[i](v[M], r)`. | Tail-call function in register `v[i[J]]` with register argument `v[M[J]]` followed by immediate argument `r[J]`; return all results after upvalue/capture cleanup. | High for call and cleanup effects |
| 170 | Close tracked open upvalues in `a`, snapshot/copy pending captured register ranges in `B`, then `return v[M](U)`. | Tail-call function in register `v[M[J]]` with immediate argument `U[J]`; return all results after upvalue/capture cleanup. | High for call and cleanup effects |
| 171 | `v[i] = v[n] / M` | Divide register value `v[n[J]]` by immediate operand `M[J]`; store the result in `v[i[J]]`. | High |
| 172 | `h=k[i]; h[5][h[4]][L] = v[n]` | Resolve the captured/upvalue cell referenced by `k[i[J]]`, then write register value `v[n[J]]` into the table held by that captured value at immediate key `L[J]`. This mutates the captured table, not the captured cell's value. | High for dereference and write; Medium for upvalue terminology |
| 173 | `h=i; z=h+n; f=v[z]; merge v[h+1..z-1] with packed args f; v[h] = _(v[h](Q(f,1,f.n)))` | Treat `v[h+n]` as a packed extra-argument table, prepend the fixed arguments from registers `h+1` through `h+n-1`, update its `.n` count, and call function `v[h]` with the combined argument list. Pass the call result through `_` and store it back in `v[h]`. The assignment to local `d=M[J]` is unused in this handler. | High for argument assembly and call target; unresolved for `_` |
| 174 | `v[M+1] = v[n]; v[M] = v[n][U]` | Prepare a method call: load receiver `v[n[J]]` into register `M+1`, then load its field `U[J]` (the method) into register `M`. The actual call occurs in a subsequent instruction. | High |
| 175 | `v[n] = v[i](L)` | Call function in register `v[i[J]]` with immediate argument `L[J]`; store the first return value in `v[n[J]]`. | High |
| 176 | `d = {n = i-n+1}; copy v[n..i] into d[1..]; v[M] = d` | Pack the inclusive VM-register range from `n[J]` through `i[J]` into a new table, store its element count in field `.n`, and place the table in register `v[M[J]]`. | High |
| 177 | Close tracked open upvalues in `a`, snapshot/copy pending captured register ranges in `B`, then `return v[i], L`. | Return register value `v[i[J]]` followed by immediate value `L[J]`, after upvalue/capture cleanup. | High |
| 178 | `J = (r <= v[i]) and J or M` | Keep the current PC when immediate `r[J]` is less than or equal to register `v[i[J]]`; otherwise branch to immediate target `M[J]` (branch condition `r > v[i]`). | High |
| 179 | `J = (v[i] <= v[M]) and J or n` | Keep the current PC when register `v[i[J]]` is less than or equal to register `v[M[J]]`; otherwise branch to immediate target `n[J]` (branch condition `v[i] > v[M]`). | High |
| 180 | `v[i] = v[n] + L` | Add immediate operand `L[J]` to register value `v[n[J]]`; store the result in `v[i[J]]`. | High |
| 181 | `v[n] = j(v[i], L)` | Apply helper `j` to register value `v[i[J]]` and immediate operand `L[J]`; store the result in `v[n[J]]`. The helper's exact operation is unresolved from this handler alone. | High for data flow; unresolved for `j` |
| 182 | Close open upvalues for registers `M[J]` and `n[J]` if entries exist in `a`; for each, save the current register value in the upvalue cell and remove the entry from `a`. | Close up to two tracked open upvalues. Unlike the return handlers, this body performs no `B`-range snapshot and does not return. | High for the state transition |
| 183 | `v[n] = L * v[i]` | Multiply immediate operand `L[J]` by register value `v[i[J]]`; store the ordinary numeric product in `v[n[J]]`. No explicit modulo-2^32 reduction appears in this handler. | High |
| 184 | `v[M](r, Q(v[i], 1, v[i].n))` | Call function in register `v[M[J]]` with immediate argument `r[J]` followed by all arguments unpacked from the packed table in `v[i[J]]`; discard the call's return values. | High |
| 185 | `v[M] = r + v[i]` | Add immediate operand `r[J]` to register value `v[i[J]]`; store the result in `v[M[J]]`. | High |
| 186 | `v[n] = k[M][i]` | Read immediate key `i[J]` from auxiliary table `k[M[J]]`; store the result in register `v[n[J]]`. | High for data flow; unresolved for the role of `k` |
| 187 | `k[i][v[n]] = v[M]` | Write register value `v[M]` into auxiliary table `k[i]` at key `v[n]`. | High |
| 188 | `v[n] = v[M](Q(v[i], 1, v[i].n))` | Call function in register `v[M[J]]` with all arguments unpacked from the packed table in `v[i[J]]`; store the first return value in register `v[n[J]]`. | High |
| 189 | `v[M](v[i], v[n])` | Call function in register `v[M[J]]` with two register arguments, `v[i[J]]` and `v[n[J]]`; discard the call's return values. | High |
| 190 | `q = q + w; in_range = (w <= 0) and (q >= I) or (w > 0 and q <= I); if in_range then v[n] = q; J = M else J = i end` | Advance the interpreter's numeric-loop state by step `w`, test the updated value against limit `I` with a sign-aware comparison, and either write the value into register `v[n[J]]` and jump to `M[J]`, or exit via `i[J]`. This is a numeric-for loop step/termination handler; the exact ownership of `q`, `w`, and `I` is interpreter state rather than ordinary VM-register operands. | High for control flow; Medium for loop mnemonic |
| 191 | `v[i] = (v[n] > M)` | Compare register value `v[n[J]]` with immediate operand `M[J]` using greater-than; store the boolean in `v[i[J]]`. | High |
| 192 | `v[i] = j(n, v[M])` | Apply helper `j` to immediate operand `n[J]` and register value `v[M[J]]`; store its result in `v[i[J]]`. The operation performed by `j` remains unresolved from this handler alone. | High for data flow; unresolved for `j` |
| 193 | `v[M] = {}` | Allocate a new empty table and store it in register `v[M[J]]`. | High |
| 194 | `v[i] = V` | Copy interpreter-local temporary/state value `V` into VM register `v[i[J]]`; this is not a read from another VM register. | High |
| 195 | Seed rolling decode state `R` from `M[J]` and `V`; for each of the next `n[J]` instruction slots, update `R` using the helper-based recurrence and merge four 7-bit fields into `i[h]`, `M[h]`, `n[h]`, and `S[h]`; then set `S[J]=57`. | Decode/rewrite a run of following instruction records using state derived from `V`; the current decoder slot becomes opcode 57 (NOP) after expansion. Helpers `j`, `u`, `C`, and `X` are not fully resolved, so the exact recurrence/encoding is left unnamed. | High for loop bounds and instruction-array writes; unresolved for recurrence semantics |
| 196 | `v[n] = (v[i] <= M)` | Compare register value `v[i[J]]` with immediate operand `M[J]` using less-than-or-equal; store the boolean in `v[n[J]]`. | High |
| 197 | `k[n][U] = L` | Write immediate operand `L[J]` into auxiliary table `k[n[J]]` at immediate key `U[J]`. | High for the write; unresolved for the role of `k` |
| 198 | `v[n] = (v[i] == v[M])` | Compare registers `v[i[J]]` and `v[M[J]]` for equality; store the boolean result in `v[n[J]]`. | High |
| 199 | `v[n] = v[M] % i` | Compute the remainder of register value `v[M[J]]` divided by immediate operand `i[J]`; store the result in `v[n[J]]`. | High |
| 200 | `h = v[i]; v[n] = _(Q(h, M, h.n))` | Take the packed table held in `v[i[J]]`, unpack/select its entries from index `M[J]` through `h.n` using helper `Q`, pass that result through helper `_`, and store the resulting value in `v[n[J]]`. The exact packing semantics of `_` are not established here. | High for selected range and data flow; unresolved for `_`/`Q` details |
| 201 | `v[i] = u(r, v[M])` | Bitwise AND of immediate operand `r[J]` with register value `v[M[J]]`, using the established helper `u`. | High |
| 202 | `v[M] = u(v[n], i)` | Bitwise AND of register value `v[n[J]]` with immediate operand `i[J]`, using the established helper `u`. | High |
| 203 | `v[n], v[n+1] = U, L` | Load immediate operands `U[J]` and `L[J]` into consecutive VM registers starting at `n[J]`. | High |
| 204 | `v[n] = v[M] .. U` | Concatenate register value `v[M[J]]` followed by immediate operand `U[J]`; store the result in `v[n[J]]`. | High |
| 205 | `h=n; z=v[h]; copy z[M+1 .. M+i] into v[h+1 .. h+i]` | Copy `i[J]` consecutive values from the packed/table value in register `v[n[J]]`, starting at source index `M[J]+1`, into VM registers beginning at `n[J]+1`. The helper `t` performs the range copy; this handler prepares a register argument/value window from a table. | High for the copy ranges; Medium for the higher-level purpose |
| 206 | `v[i] = n + v[M]` | Add immediate operand `n[J]` to register value `v[M[J]]`; store the result in `v[i[J]]`. | High |
| 207 | `v[n] = H` | Copy interpreter-local value/table `H` into VM register `v[n[J]]`; the handler stores the whole `H` reference, not an indexed element. | High for data flow; unresolved for the role of `H` |
| 208 | `h=k[n]; h[5][h[4]] = v[M]` | Resolve the captured/upvalue cell referenced by `k[n[J]]` and assign register value `v[M[J]]` to the captured variable itself. This updates the upvalue cell's stored value rather than indexing a table held by that value. | High for dereference and assignment; Medium for upvalue terminology |
| 209 | `v[i](L, v[n])` | Call function in register `v[i[J]]` with immediate argument `L[J]` followed by register argument `v[n[J]]`; discard the call's return values. | High |
| 210 | `h=M; R=i; d=n; z=v[h]; f=h+R; F=v[f]; copy z[d+1 .. d+R-1] into v[h+1 .. f-1]; copy z[d+R .. d+R+F.n-1] into F[1 .. F.n]` | Reorganize a packed argument/value table: copy the fixed segment into consecutive VM registers after base register `M`, then copy the remaining segment into the packed table held in register `v[M+i]`, preserving that table's `.n` count. This is a bulk argument-window/vararg preparation operation; no function call occurs in this handler. | High for the observed copy ranges; Medium for the higher-level label |
| 211 | Close tracked open upvalues in `a`, snapshot/copy pending captured register ranges tracked in `B`, then `return v[M], v[n], v[i]`. | Return three VM register values, in order `v[M[J]]`, `v[n[J]]`, and `v[i[J]]`, after upvalue/capture cleanup. | High |
| 212 | `h=k[n]; v[M] = h[5][h[4]][U]` | Resolve the captured/upvalue cell referenced by `k[n[J]]`, then read immediate key `U[J]` from the table held by that captured value; store the field in `v[M[J]]`. | High for dereference and read; Medium for upvalue terminology |
| 213 | Close tracked open upvalues in `a`, snapshot/copy pending captured register ranges in `B`, then `return Q(v, M, M+n-1)`. | Return the consecutive VM-register range beginning at `v[M[J]]` and ending at `v[M[J]+n[J]-1]` (a total of `n[J]` values), after upvalue/capture cleanup. `Q` expands the selected register range into multiple return values. | High |
| 214 | `v[M](v[n], U)` | Call function in register `v[M[J]]` with register argument `v[n[J]]` followed by immediate argument `U[J]`; discard the call's return values. | High |
| 215 | Close all tracked open upvalues in `a`, snapshot/copy pending captured register ranges tracked in `B`, then `h=M[J]; return Q(v,h,h+n[J]-1)`. | Return `n[J]` consecutive VM-register values starting at `v[M[J]]` as multiple return values, after open-upvalue and captured-range cleanup. The handler body is byte-for-byte identical for opcodes 215–255; opcode 215 is the canonical entry for this shared handler. | High for register range and cleanup; alias relation confirmed by identical handler bodies |
| 216 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 217 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 218 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 219 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 220 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 221 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 222 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 223 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 224 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 225 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 226 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 227 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 228 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 229 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 230 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 231 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 232 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 233 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 234 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 235 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 236 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 237 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 238 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 239 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 240 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 241 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 242 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 243 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 244 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 245 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 246 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 247 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 248 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 249 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 250 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 251 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 252 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 253 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 254 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
| 255 | Same handler body as opcode 215. | Alias of opcode 215: closes open upvalues, snapshots captured ranges, then returns the consecutive register range beginning at `v[M[J]]` with count `n[J]`. | High — identical handler body |
## Notes

- Opcode 6 copies **from** the vararg list **into** the VM register array.
- Opcode 17 is the inverse-looking half of opcode 64 (`W = v[i]`): opcode 64 reads a register into the internal temporary `W`, while opcode 17 writes `W` back to a register. This does not, by itself, establish what `W` represents at a higher level.
- Opcode 18 and opcode 25 are distinct: 18 is a tail-call that returns the callee's results; 25 is a plain no-argument call whose results are discarded.
- Opcode 21 and opcode 106 are also distinct: 21 takes its function from `v[n]` and an immediate argument `U`; 106 takes its function from `v[M]` and its argument from `v[n]`.
- Opcode 12 remains a provisional semantic label pending examination of its surrounding frame setup/return paths.
- Refresh the pending-handler inventory with `python tools/list_remaining_luraph_opcodes.py` from the repository root after restoring the VM chunk in `/tmp`.
