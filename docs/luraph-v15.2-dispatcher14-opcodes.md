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

This is an evolving reverse-engineering note, not a claim that every listed opcode occurs in the payload. The dispatcher scanner previously reported **108 source-location groups**, but that structural count must not be confused with the number of opcode values used at runtime. The resolver and inventory generator have since been corrected to walk past local setup statements and to keep mixed mapped/unmapped groups unresolved. Regenerate the pending inventory after pulling the latest branch revision; older reports may incorrectly label unrelated opcode values as aliases.

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
| 49 | `v[M] = v[i][n]` | Read key `n` from table/value in register `v[i]` and store the result in `v[M]`. | High |
| 50 | `v[i] = e[r][L]` | Read `e[r][L]` from the nested environment table and store it in `v[i]`. | High for the access |
| 51 | `v[M], v[M+1] = i, r` | Load two immediate operands into consecutive VM registers starting at `M`. | High |
| 52 | `q, I, w, G = O[5], O[7], O[6], O[9]; O = O[8]` | Restore interpreter state fields from the saved frame and pop the frame chain. | High for the state restoration; Medium for frame naming |
| 53 | `v[M] = _(v[M](Q(v, M+1, M+i)))` | Call the function in register `M` with `i` arguments from the following registers and store the first return value back in `v[M]`. | High |
| 54 | `v[M] = u(v[n], U)` | Bitwise AND of register `v[n]` with immediate operand `U` (same normalization/bitwise helper as opcode 7). | High, based on the established helper use |
| 55 | `v[M] = _(v[n](v[i]))` | Call the function in `v[n]` with one argument from `v[i]`; pass the call result through helper `_` and store that helper's result in `v[M]`. The exact transformation performed by `_` is not inferred from this line alone. | High for call/argument/data flow; unresolved for `_` |
| 59 | `v[M][r] = U` | Write immediate `U` into the table held in register `v[M]`, using immediate key `r`. | High |
| 60 | `h = k[i]; h[5][h[4]][v[M]] = v[n]` | Resolve the captured/upvalue cell referenced by `k[i]`, then write `v[n]` into the table held by that captured value at key `v[M]`. This mutates the referenced table; it does not replace the upvalue cell itself. | High for the dereference and write |
| 61 | Close tracked open upvalues in `a`, snapshot pending captured register ranges in `B`, then `return v[i]`. | VM return of the value in register `v[i]`, preceded by upvalue/capture cleanup. The precise abstraction represented by `B` remains provisional. | High for the return and cleanup effects |
| 63 | `v[M] = A(U, v[n])` | Call helper `A` with immediate `U` and register value `v[n]`; store its result in `v[M]`. The helper's semantic operation is not established by this handler alone. | High for data flow; unresolved for `A` |
| 64 | `W = v[i]` | Copy register `v[i]` into the interpreter-local temporary/state variable `W`; this does not write to a VM register. | High |
| 65 | `my = M; J = n + 1; break` | Store operand `M` in interpreter-local `my`, set the next PC to `n+1`, and exit the current enclosing loop. The broader meaning of `my` depends on the loop's caller/context. | High for the visible effects; Medium for the higher-level purpose |
| 66 | `J = (v[i] < L) and J or n` | Keep the current PC when `v[i] < L`; otherwise branch to `n` (branch condition `v[i] >= L`). | High |
| 67 | `v[n] = (v[M] ~= U)` | Compare register `v[M]` with immediate `U` for inequality; store the boolean in `v[n]`. | High |
| 68 | `v[M] = _(v[i]())` | Call the function in `v[i]` with no arguments; pass the call result through helper `_` and store that helper's result in `v[M]`. The exact transformation performed by `_` is not inferred from this line alone. | High for call/data flow; unresolved for `_` |
| 69 | Close tracked open upvalues in `a`, snapshot pending captured register ranges in `B`, then `return L, r`. | VM return of the two immediate values `L[J]` and `r[J]`, preceded by upvalue/capture cleanup. The precise abstraction represented by `B` remains provisional. | High for the return and cleanup effects |
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
| 47 | `v[M] = (i * v[n]) mod 2^32` | Low 32 bits of immediate × register multiplication. | High |
| 48 | `v[M] = v[n] - v[i]` | Register subtraction. | High |
| 56 | `v[n] = (v[i] * v[M]) mod 2^32` | Low 32 bits of register × register multiplication. | High |
| 57 | No operation. | NOP. | High |
| 58 | `J = v[n]` | Unconditional jump to the address held in a register. | High |
| 62 | `v[M] = i` | Load immediate into a VM register. | High |
| 70 | Loads `H`, `S`, `n`, and `i` into four consecutive registers starting at `n[J]`; advances `J` by 3. | Special VM environment/helper setup instruction. | High |
| 95 | `J = v[M] and i or n` | Truthiness branch based on register `v[M]`. | High |
| 99 | `v[M], v[M+1] = v[n], v[i]` | Copy two registers into consecutive destination registers (parallel assignment; not a swap). | High |
| 104 | `v[M] = v[i]()` | Call function in `v[i]` without arguments; store the first return value in `v[M]`. | High |
| 106 | `v[M](v[n])` | Call function in `v[M]` with one register argument; discard results. | High |
| 136 | `J = M` | Unconditional jump to immediate target. | High |
| 187 | `k[i][v[n]] = v[M]` | Write register value `v[M]` into auxiliary table `k[i]` at key `v[n]`. | High |

## Notes

- Opcode 6 copies **from** the vararg list **into** the VM register array.
- Opcode 17 is the inverse-looking half of opcode 64 (`W = v[i]`): opcode 64 reads a register into the internal temporary `W`, while opcode 17 writes `W` back to a register. This does not, by itself, establish what `W` represents at a higher level.
- Opcode 18 and opcode 25 are distinct: 18 is a tail-call that returns the callee's results; 25 is a plain no-argument call whose results are discarded.
- Opcode 21 and opcode 106 are also distinct: 21 takes its function from `v[n]` and an immediate argument `U`; 106 takes its function from `v[M]` and its argument from `v[n]`.
- Opcode 12 remains a provisional semantic label pending examination of its surrounding frame setup/return paths.
- Refresh the pending-handler inventory with `python tools/list_remaining_luraph_opcodes.py` from the repository root after restoring the VM chunk in `/tmp`.
