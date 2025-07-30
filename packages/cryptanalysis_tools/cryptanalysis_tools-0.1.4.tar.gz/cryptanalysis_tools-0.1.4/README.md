> :warning: **警告**
>
> 本项目仅作个人学习使用，不可用于生产环境，否则后果自负。
>
> This library is only for learning purposes and can ```not``` be used in ```production``` environments. Otherwise, you will be at your own risk.

> :memo: **可参考 tests 中的使用方法**

# Crypto
## SM2
### sign
> **SM2的裸签名，类似ECC，直接用这个签名不符合国标要求，除非自己特意构造的**
> **data即e，没有预处理计算ZA操作，没有SM3，因为在底下的sm2_sm3中有，**
```python
sign(self, data: bytes, private_key: int, k: int | None = None)
```

### verify
```python
verify(self, signature: asn1str | Tuple[int, int], data: bytes, public_key: Tuple[int, int])
```

### compute_ZA
```python
compute_ZA(self, public_key: Tuple[int, int], ID: str | None = None)
```

### sign_with_sm3
> **符合国标的签名**
> **SM2真正的签名对象如下**
> **tobesign = sm3.hash(ZA + data)， ZA = compute_ZA(public_key, ID)**
```python
sign_with_sm3(self, data: bytes, private_key: int, public_key: Tuple[int, int], ID: str | None = None, randomk: int | None = None)
```

### verify_with_sm3
```python
verify_with_sm3(self, signature: asn1str | Tuple[int, int], data: bytes, public_key: Tuple[int, int], ID: str | None = None)
```

### encrypt
```python
encrypt(self, msg: bytes, public_key: Tuple[int, int], k: int | None = None)
```

### decrypt
```python
decrypt(self, cipher_txt: asn1str, private_key: int)
```

### recover_privateKey_by_kAndrs
> **已知秘密随机数k，一组r，s（即签名值）,可恢复sm2私钥。**
```python
recover_privateKey_by_kAndrs(self, k: int, r: int, s: int)
```

### recover_privateKey_by_fixedk_and_2rs
> **无需知道k的具体值，但知道k是固定值，通过两组rs（即签名值），可恢复sm2私钥。**
```python
recover_privateKey_by_fixedk_and_2rs(self, r1: int, s1: int, r2: int, s2: int)
```

### recover_publicKeys_by_eAndrs
> **纯数学公式计算，知道一组签名值rs与e的值，可恢复公钥，满足条件的公钥可能存在多个。e可能是原消息m，或者是经过hash预处理的e，具体看怎么签的名**
```python
recover_publicKeys_by_eAndrs(self, e: int, r: int, s: int)
```

### is_same_k
```python
is_same_k(self, r1, e1, r2, e2)
```

### recover_private_key_by_liner_k
> **如果k的随机性是线性的，k2 = ak1 + bG，且知道线性参数，可通过两组rs，恢复sm2私钥，故固定k是一种特殊情况**
```python
recover_private_key_by_liner_k(self, r1: int, s1: int, r2: int, s2: int, a: int, b: int)
```

### forge_e_signature
> **纯数学公式计算，t是 r + s，伪造e的签名，说是伪造其实是恢复e而已，已知一组签名值rs及公钥，计算对哪个e进行签名。故可以随机产生一组r，s，然后计算得到一个e，使得验签通过**
```python
forge_e_signature(self, public_key: Tuple[int, int], s: int, t: int)
```

## SM3
### hash
> **sm3的hash方法，有点想把str输入移除了**
```python
hash(msg: bytes | str) -> bytes
```

## SM4
> **纯SM4算法加解密实现，不涉及工作模式，所以不存在IV与Padding值**
> **分组密码自身只能加密长度等于密码分组长度的单块数据**
### encrypt
```python
encrypt(plaintext: bytes, key: bytes) -> bytes
```

### decrypt
```python
decrypt(cipher: bytes, key: bytes) -> bytes
```

## utils
### kdf
> **密钥派生函数**

### rotl
> **将x循环左移n位**
```python
rotl(x, n)
```

### types
```python
asn1str: TypeAlias = str
```

# TODO :dart:
- [ ] sm2协同签名
- [ ] CBC-MAC不定长攻击
- [ ] 对称密码逆序流程
- [x] M-D 结构 hash 长度拓展攻击
- [ ] padding oracle 填充攻击
- [ ] hash collision 哈希碰撞
