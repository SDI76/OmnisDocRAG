_chartoutf8()isunicode() locale() nfc() nfd()_ ord() _unichr() unicode() uniconv() utf8tochar()_ 

**Number** 

## **Functions** 

_abs() fact() fmtdp() int()_ iseven() isodd() _mod() pwr() rnd() sqr()_ 

**==> picture [21 x 8] intentionally omitted <==**

**----- Start of picture text -----**<br>
abs()<br>**----- End of picture text -----**<br>


|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Number_|YES|All|



## **Syntax** 

**abs** (number) 

## **Description** 

Returns the magnitude of a real _number_ ignoring its positive or negative sign. 

## **Example** 

```
Calculate lResult as abs(1002)
# returns 1002
Calculate lResult as abs('-203.45')
# returns 203.45
```

```
Calculate lResult as abs('12ABC')
# returns 0
```

## **acos()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Trigonometric_|YES|All|



## **Syntax** 

**acos** ( _number_ ) 

## **Description** 

Returns the arc cosine of a _number_ in the range 0 to 180 degrees (0 to pi radians if #RAD is true), or returns 0 if the number is not in the range -1 to 1. 

8 



## **Example** 

```
Calculate lResult as acos(spr(2)/2)
# returns 45
```

## **alt()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|YES|All|



## **Syntax** 

## **alt** () 

## **Description** 

Returns true if the Alt or Option key is being pressed. 

## **ann()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Financial_|NO|All|



## **Syntax** 

**ann** (rate,nper,pmt,pv,fv[,prd]) 

## **Description** 

Evaluates an unknown for an annuity and returns the result. 

The first five arguments are mandatory, but you can replace any one of them with ‘?’ which is the unknown value returned by the function. 

Parameters: _rate_ is the interest rate per payment period; _nper_ is the number of payment periods, which should be an integer greater than zero; _pmt_ is the payment made to you (or by you) at the end of each period; _pv_ is the amount paid to you (or by you) at the start of the first period; _fv_ is the amount paid to you (or by you) at the end of the final period; _prd_ is optional and represents a specific period which must be between 1 and _nper_ ; it is used for obtaining the split of interest and capital payments in a period. 

The convention is that positive values for _pmt, pv_ and _fv_ denote a payment made _to you_ , and negative amounts denote a payment made _by you_ . It is important to ensure that _rate, nper_ and _pmt_ all refer to the same period length. The annuity is evaluated so that the sum of all payments made to you (or by you) when compounded at the interest rate evaluates to zero. 

The following example shows that, a 25 year mortgage for $30000 at 11% pa interest payable monthly in arrears has monthly payments, paid by you, is equal to: 

## **Example** 

```
Calculate lAmount as rnd(ann(.11/12,25*12,'?',30000,0),2)
# returns -294.03
```

## **anna()** 

9 



Function group Execute on client Platform(s) _Financial_ NO All 

## **Syntax** 

**anna** (rate,nper,pmt,pv,fv) 

## **Description** 

Evaluates an unknown for an annuity in advance and returns the result. 

This function works in the same way as the _ann()_ function except that the annuity is calculated in advance. The payments are assumed to be made at the start of each period instead of the end of each period. 

The following example shows what the monthly payment is, using the same arguments as those used for the example for _ann(),_ but using the **anna()** function, where the mortgage payments are assumed to be made in advance. 

## **Example** 

```
Calculate lAmount as rnd(anna(.11/12,25*12,'?',30000,0),2)
# returns -291.36
```

## **asc()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_String_|NO|All|



## **Syntax** 

**asc** (string,position) 

## **Description** 

Returns the ASCII or Unicode value of the character at the _position_ in the _string_ . The first _position_ in the _string_ is 1. 

The value returned for ASCII characters is between 0 and 255, or -1 if _position_ is less than 1 or greater than the length of _string_ . 

## **Example** 

```
Calculate lResult as asc('Quantity',1)
# returns 81, that is the ASCII value of the 1st character Q
```

```
Calculate lResult as asc('Car',3)
# returns 114, that is the ASCII value of the 3rd character r
```

```
Calculate lResult as asc('Train',9)
```

```
# returns -1 because 9 is greater than the length of the string
```

## **asin()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Trigonometric_|YES|All|



10 



**Syntax** 

**asin** ( _number_ ) 

## **Description** 

Returns the arc sine of a _number_ in the range -90 to 90 degrees (-pi/2 to pi/2 radians if #RAD is true), or returns 0 if the number is not in the range -1 to 1. 

## **Example** 

```
Calulate lResult as asin(sqr(3)/2)
# returns 60
```

## **atan()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Trigonometric_|YES|All|



**Syntax atan** ( _number_ ) 

## **Description** 

Returns the arc tangent of a _number_ in the range -90 to 90 degrees (-pi/2 to pi/2 radians if #RAD is true). 

## **Example** 

```
Calculate lResult as atan(1)
# returns 45
```

## **atan2()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Trigonometric_|YES|All|
|**Syntax**|||
|**atan2**(_y,x_)|||



## **Description** 

Returns the arc tangent of the point y,x coordinates. 

## **Example** 

```
Calculate lResult as atan2(1,1)
# returns 45
```

11 



## **avgc()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_List_|NO|All|



## **Syntax** 

**avgc** (listname,column[,ignore-nulls]) 

## **Description** 

Returns the average value for a list column specified by _listname_ and _column_ . avgc() can only be used with columns defined using variables so it cannot be used with lists defined from a SQL class. 

If you set _ignore-nulls_ to 1, null values are ignored and not counted. If you omit this parameter or it evaluates to zero, nulls are treated as zero values and are counted. 

## **Example** 

```
Calculate lResult as avgc(lList,lCol1,1)
```

```
# returns the average for lCol1 not including null or zero values
```

## **basecolor()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|NO|All|



**Syntax basecolor** ( _color_ ) 

## **Description** 

Returns the 32bit RGB or color constant without any alpha value, extracted from the supplied color property value. 

## **bdif()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|Binary Field|NO|All|



## **Syntax** 

**bdif** (oldbinary,newbinary) 

## **Description** 

Returns a binary representation of the differences between _oldbinary_ and _newbinary_ . 

It is useful for comparing different versions of the same file, whether it is an Omnis library, external component, picture or text file, and so on. 

## **Example** 

```
Calculate lBinDiff as bdif(lOldBinary,lNewBinary)
```

12 



**binchecksum()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|Binary Field|NO|All|



## **Syntax** 

## **binchecksum** ( _binary_ ) 

## **Description** 

Calculates an integer checksum for a _binary_ field and returns the result. 

Omnis generates the checksum by summing the bytes of the _binary_ field, using a 32 bit number, ignoring overflow. 

## **Example** 

```
Calculate lCheckSum as binchecksum(lBinary)
```

## **bincompare()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|Binary Field|NO|All|



## **Syntax** 

**bincompare** (binary1,binary2) 

## **Description** 

Compares two binary fields, _binary1_ and _binary2_ . Returns true if they are equal and false if they are not. 

Fields of different length are _not_ equal, meaning that the rule about extending the length of the shortest field does not apply in this case. 

## **Example** 

```
Calculate lStatus as bincompare(lBinary1,lBinary2)
```

## **binfrombase32()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Binary Field_|NO|All|



## **Syntax** 

**binfrombase32** (vData) 

## **Description** 

Decodes the binary or character _vData_ from BASE32 and returns the resulting binary data. Returns #NULL if _vData_ is not valid BASE32 or an error occurs. 

13 



**binfrombase64()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Binary Field_|NO|All|



## **Syntax** 

**binfrombase64** (vData[,bURLEncoding=kFalse, bExpectPadding=kTrue, bStripWhitespace=kFalse]) 

## **Description** 

Decodes the binary or character _vData_ from BASE64 and returns the resulting binary data. Returns NULL if _vData_ is not valid BASE64. 

Pass _bURLEncoding_ as kTrue to decode the URL-safe form of base64. 

Pass _bExpectPadding_ as kFalse to not expect any padding in the base64. Typically, this would be passed as kFalse when using URLsafe encoding. 

Pass _bStripWhitespace_ as kTrue to strip whitespace from the input data (defaults to kFalse). 

## **binfromhex()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Binary Field_|NO|All|



## **Syntax** 

**binfromhex** ( _string_ ) 

## **Description** 

Returns a binary field value generated from the specified character _string_ , typically generated using _bintohex_ (). 

The character _string_ encodes a hexadecimal value in ASCII. The _string_ must not contain a leading 0x or 0X. 

## **Example** 

```
Calculate lBinary as binfromhex(lString)
```

## **binfromint32()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Binary Field_|NO|All|



## **Syntax** 

**binfromint32** ( _int32_ ) 

## **Description** 

Returns a binary field value containing the binary representation of the 32 bit integer _int32_ . 

14 



**binfromint64()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Binary Field_|NO|All|



## **Syntax** 

**binfromint64** ( _int64_ ) 

## **Description** 

Returns a binary field value containing the binary representation of the 64 bit integer _int64_ . 

## **binlength()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Binary Field_|NO|All|



## **Syntax** 

**binlength** ( _binary_ ) 

## **Description** 

Returns the length of a _binary_ field in bytes. 

## **Example** 

```
Calculate lLength as binlength(lBinary)
```

## **binsearch()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Binary Field_|NO|All|



## **Syntax** 

**binsearch** (binary1,binary2[,start-from]) 

## **Description** 

Returns the zero-based position of _binary1_ in _binary2_ , or returns -1 if not found. 

_start-from_ is the zero-based index of the byte in _binary2_ where the search is to start. If omitted, _start-from_ defaults to zero at the start of _binary2._ 

## **Example** 

```
Calculate lPosition as binsearch(lBinary1,lBinary2,5)
```

15 



**bintobase32()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Binary Field_|NO|All|



## **Syntax** 

**bintobase32** (vData) 

## **Description** 

Encodes _vData_ as BASE32 and returns the binary result. _vData_ can be either binary or character. If _vData_ is character, Omnis converts it to UTF-8 before encoding it as BASE32. Returns #NULL if an error occurs. 

## **bintobase64()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Binary Field_|NO|All|



## **Syntax** 

**bintobase64** (vData[,bURLEncoding=kFalse,bAddPadding=kTrue]) 

## **Description** 

Encodes _vData_ as BASE64 and returns the result. _vData_ can be either binary or character. If _vData_ is character, Omnis converts it to UTF-8 before encoding it as BASE64. 

Pass _bURLEncoding_ as kTrue to use the URL-safe form of base64. 

Pass _bAddPadding_ as kFalse to exclude the padding from the base64 (the one or two = characters appended to the end of the encoded data). Typically, this would be passed as kFalse when using URL-safe encoding. 

## **bintohex()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Binary Field_|NO|All|



## **Syntax** 

**bintohex** ( _binary_ ) 

## **Description** 

Returns a character string representing the value of a _binary_ field, in ASCII hexadecimal. 

## **Example** 

```
Calculate lString as bintohex(lBinary)
```

## **bintoint32()** 

16 



|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Binary Field_|NO|All|



## **Syntax** 

**bintoint32** ( _binary_ ) 

## **Description** 

Returns a 32 bit integer value from the first 4 bytes of a _binary_ field. 

## **bintoint64()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Binary Field_|NO|All|



## **Syntax** 

**bintoint64** ( _binary_ ) 

## **Description** 

Returns a 64 bit integer value from the first 8 bytes of a _binary_ field. 

## **bitand()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Binary Field_|NO|All|



## **Syntax** 

**bitand** (binary1,binary2) 

## **Description** 

Performs an AND operation on _binary1_ and _binary2_ , and returns the result. 

## **Example** 

```
Calculate lNewBinary as bitand(lBinary1,lBinary2)
```

## **bitclear()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Binary Field_|NO|All|



## **Syntax** 

**bitclear** (binary1,firstbitnumber,lastbitnumber) 

17 



## **Description** 

Clears a range of bits (all bits with numbers >= _firstBitNumber_ and <= _lastBitNumber_ ) operating directly on _binary_ . Returns a Boolean (true for success). 

The function operates directly on the _binary1_ argument, and returns 1 for success and 0 for failure. If the bit numbers identify some bits which are outside the current length of the binary field, Omnis extends the field by appending bytes with value zero, and clears the bits. 

The first parameter can be a Binary or an Integer; in the case of Binary, you need to provide a variable, and not the result of a calculation. 

## **Example** 

```
Calculate lStatus as bitclear(lBinary1,lFirstBitNumber,lLastBitNumber)
```

## **bitfirst()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Binary Field_|NO|All|



## **Syntax** 

**bitfirst** ( _binary_ ) 

## **Description** 

Returns the number of the most significant bit with value 1 in a _binary_ field. 

The parameter can be a Binary or an Integer; in the case of Binary, you need to provide a variable, and not the result of a calculation. The following example sets lNumber to the bit number of the first bit set to 1. If all bits are zero, **bitfirst()** returns -1. 

## **Example** 

```
Calculate lNumber as bitfirst(lBinary)
```

## **bitmid()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Binary Field_|NO|All|



## **Syntax** 

**bitmid** (binary,firstbitnumber,lastbitnumber) 

## **Description** 

Returns a binary value identified as a range of bits of a _binary_ field, that is, bitmid() extracts the bits with numbers >= _firstBitNumber_ and <= _lastBitNumber_ . 

The first parameter can be a Binary or an Integer; in the case of Binary, you need to provide a variable, and not the result of a calculation. 

In the following example, bit _lFirstBitNumber_ of _lBinary1_ becomes bit zero of _lBinary2_ , and so on. 

## **Example** 

```
Calculate lBinary2 as bitmid(lBinary1,lFirstBitNumber,lLastBitNumber)
```

18 



## **bitnot()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Binary Field_|NO|All|



## **Syntax** 

**bitnot** ( _binary_ ) 

## **Description** 

Performs a 1’s complement operating directly on _binary_ . Returns a Boolean (true for success). 

The function operates directly on the argument _binary1_ , and returns 1 for success and 0 for failure. 

The parameter can be a Binary or an Integer; in the case of Binary, you need to provide a variable, and not the result of a calculation. 

## **Example** 

```
Calculate lStatus as bitnot(lBinary)
```

## **bitor()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Binary Field_|NO|All|
|**Syntax**|||
|**bitor**(binary1,binary2)|||



## **Description** 

Performs an inclusive-OR on _binary1_ and _binary2_ , and returns the result. 

## **Example** 

```
Calculate lStatus as bitor(lBinary1,lBinary2)
```

## **bitrotatel()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Binary Field_|NO|All|



## **Syntax** 

**bitrotatel** ( _binary,count_ ) 

## **Description** 

Rotates a _binary_ field to the left, by number of bits specified in _count_ . Operates directly on _binary_ . Returns a Boolean (true for success). 

The function operates directly on the argument, and returns 1 for success and 0 for failure. The vacated bits are replaced by the bits shifted off the left-hand end. If the specified number of bits is greater than the bit-length of the field, Omnis returns 0, and the field is unchanged. 

The first parameter can be a Binary or an Integer; in the case of Binary, you need to provide a variable, and not the result of a calculation. 

19 



## **Example** 

```
Calculate lStatus as bitrotatel(lBinary,lCount)
```

## **bitrotater()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Binary Field_|NO|All|



## **Syntax** 

**bitrotater** ( _binary,count_ ) 

## **Description** 

Rotates a _binary_ field to the right by number of bits specified in _count_ .Operates directly on _binary_ .Returns a Boolean (true for success). 

The function operates directly on the argument, and returns 1 for success and 0 for failure. The vacated bits are replaced by the bits shifted off the right-hand end. If the specified number of bits is greater than the bit-length of the field, Omnis returns 0, and the field is unchanged. 

The first parameter can be a Binary or an Integer; in the case of Binary, you need to provide a variable, and not the result of a calculation. 

## **Example** 

```
Calculate lStatus as bitrotater(lBinary,lCount)
```

## **bitset()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Binary Field_|NO|All|



## **Syntax** 

**bitset** (binary,firstbitnumber,lastbitnumber) 

**bitset** (binary,firstbitnumber[,lastbitnumber]) 

## **Description** 

Sets a range of bits (all bits with numbers >= _firstBitNumber_ and <= _lastBitNumber_ ) operating directly on _binary_ . Returns a Boolean (true for success). 

The function operates directly on the argument, and returns 1 for success and 0 for failure. If the bit numbers identify some bits which are outside the current length of the binary field, Omnis extends the field by appending bytes with value zero, and sets the bits. 

The first parameter can be a Binary or an Integer; in the case of Binary, you need to provide a variable, and not the result of a calculation. 

If _lastBitNumber_ is omitted, the value in _firstBitNumber_ is used allowing you to set a single bit. 

## **Example** 

```
Calculate lStatus as bitset(lBinary,lFirstBitNumber,lLastBitNumber)
```

20 



## **bitshiftl()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Binary Field_|NO|All|



## **Syntax** 

**bitshiftl** (binary,count) 

## **Description** 

Shifts a _binary_ field to the left by a number of bits specified in _count_ . Operates directly on _binary_ . Returns a Boolean (true for success). 

The function operates directly on the argument, and returns 1 for success and 0 for failure. Vacated bits become zero. Bits shifted past bit 0 are lost. 

The first parameter can be a Binary or an Integer; in the case of Binary, you need to provide a variable, and not the result of a calculation. 

## **Example** 

```
Calculate lStatus as bitshiftl(lBinary,lCount)
```

## **bitshiftr()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Binary Field_|NO|All|



## **Syntax** 

**bitshiftr** (binary,count) 

## **Description** 

Shifts a _binary_ field to the right by a number of bits specified in _count_ . Operates directly on _binary_ . Returns a Boolean (true for success). 

The function operates directly on the argument, and returns 1 for success and 0 for failure. Vacated bits become zero. Bits shifted past the right-most bit are lost. 

The first parameter can be a Binary or an Integer; in the case of Binary, you need to provide a variable, and not the result of a calculation. 

## **Example** 

## `Calculate lStatus as bitshiftr(lBinary,lCount)` 

## **bittest()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Binary Field_|NO|All|



## **Syntax** 

**bittest** (binary,firstbitnumber,lastbitnumber) 

**bittest** (binary,firstbitnumber[,lastbitnumber]) 

21 



## **Description** 

Tests a range of bits (all bits with numbers >= _firstBitNumber_ and <= _lastBitNumber_ ) in _binary_ . _binary_ must either be a binary field, or a long integer, you cannot use a function in the first argument. Returns a Boolean (true if at least one bit in the range is set). 

If any are 1, the function returns 1, otherwise it returns zero. 

The first parameter can be a Binary or an Integer; in the case of Binary, you need to provide a variable, and not the result of a calculation. 

If _lastBitNumber_ is omitted, the value in _firstBitNumber_ is used allowing you to test a single bit. 

## **Example** 

```
Calculate lStatus as bittest(lBinary,lFirstBitNumber,lLastBitNumber)
```

## **bitxor()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Binary Field_|NO|All|



## **Syntax** 

**bitxor** (binary1,binary2) 

## **Description** 

Performs an exclusive-OR (XOR) on _binary1_ and _binary2_ , and returns the result. 

## **Example** 

```
Calculate lNewBinary as bitxor(lBinary1,lBinary2)
```

## **br()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_String_|YES|All|



## **Syntax** 

**br** () 

## **Description** 

Returns a style sequence that can be used as a line break in styled text when using the JavaScript client (equivalent to style(kEscJsNewline)). 

## **bundif()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Binary Field_|NO|All|



## **Syntax** 

**bundif** (differences,binary) 

22 



## **Description** 

Restores an older version of a _binary_ file using the _differences_ created by the _bdif_ () function. The differences must be passed to an older version of the same _binary_ file. 

## **Example** 

```
Calculate lBinary2 as bundif(lBinDiff,lBinary1)
```

## **bytecon()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Binary Field_|NO|All|



## **Syntax** 

**bytecon** (binary1,binary2) 

## **Description** 

Concatenates two binary fields _binary1_ and _binary2_ , and returns the result. 

Note that **bytecon()** concatenates _binary2_ on to the end of _binary1_ . 

## **Example** 

```
Calculate lNewBinary as bytecon(lBinary1,lBinary2)
```

## **byteget()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Binary Field_|NO|All|



## **Syntax** 

**byteget** (binary,byteNumber) 

## **Description** 

Returns the value (0-255) of the byte at the specified _byteNumber_ in _binary_ . Returns -1 if an error occurs. 

## **bytemid()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Binary Field_|NO|All|



## **Syntax** 

**bytemid** (binary1,firstbytenumber,lastbytenumber) 

23 



## **Description** 

Returns a binary value identified as a range of bytes in a binary field (all bytes between _firstByteNumber_ and _lastByteNumber_ inclusive). 

The following example sets _lBinary2_ to the value generated by extracting bytes l _FirstByteNumber_ to _lSecondByteNumber_ inclusive of _lBinary1_ . Thus byte 0 of _lBinary2_ becomes byte _lFirstByteNumber_ of _lBinary1,_ and so on. 

## **Example** 

```
Calculate lBinary2 as bytemid(lBinary1,lFirstByteNumber,lSecondByteNumber)
```

## **byteset()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Binary Field_|NO|All|



## **Syntax** 

**byteset** (binary,bytenumber,value) 

## **Description** 

Sets byte _byteNumber_ in _binary_ to the specified _value_ , operating directly on _binary_ . Returns a Boolean (true for success). 

The function operates directly on the argument, and returns 1 for success and 0 for failure. 

## **Example** 

```
Calculate lStatus as byteset(lBinary1,lByteNumber,lValue)
```

## **callprivate()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|YES|All|



## **Syntax** 

**callprivate** (method[,parameters…]) 

## **Description** 

Calls the private _method_ with the specified _parameters_ and returns its return value. 

## **cap()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_String_|YES|All|



## **Syntax** 

**cap** (string) 

24 



## **Description** 

Returns the capitalized representation of a _string_ , that is, the first letter of each and every word in the string is capitalized. 

## **Example** 

```
Calculate lResult as cap('gRaVeS, hutton, MONKS')
# returns 'Graves, Hutton, Monks'
```

```
Calculate lResult as cap('on the 8TH day')
# returns 'On the 8th Day'
```

## **cdif()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Class_|NO|All|



## **Syntax** 

**cdif** (oldclass,newclass) 

## **Description** 

Returns a list of differences between two classes _oldclass_ and _newclass_ , the first parameter is the older class, and the second parameter is the newer class. 

The **cdif()** function returns a binary representation of differences between two Omnis library classes of the same type, for example, you can compare two versions of the same window class. 

An #ERRCODE value of 8095 means that the classes are identical. If an error occurs during execution, the flag is set to false, and #ERRCODE and #ERRTEXT will contain the error number and text. 

## **Example** 

```
Calculate lOldClass as $windows.window1.$classdata
Calculate lNewClass as $windows.window2.$classdata
Calculate lDiffList as cdif(lOldClass,lNewClass)
```

## **charcount()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_String_|YES|All|



## **Syntax** 

**charcount** ( _string_ , _char_ ) 

## **Description** 

Returns the number of occurrences of the character _char_ in the _string_ . 

25 



## **Example** 

```
Calculate lString as 'Omnis Studio is great'
Calculate lCount as charcount(lString,'i')
# returns 3
```

```
If charcount(lString,'i')>2
# returned True
End If
```

## **chartoutf8()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Unicode_|NO|All|



## **Syntax** 

**chartoutf8** ( _string_ ) 

## **Description** 

Returns the binary value which is the UTF-8 encoding of the character _string_ . 

## **chk()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_String_|NO|All|



## **Syntax** 

**chk** (string1,string2,string3) 

## **Description** 

Returns true or false depending on a character-by-character comparison of _string1_ with _string2_ and _string3_ using the ASCII value of each character for the basis of the comparison. 

Firstly, each character of _string2_ is compared with the corresponding character of _string1_ to ensure that, for each character, _string2_ <= _string1_ . A character is said to be less than or greater than another character if its ASCII code is less than or greater than the ASCII code of the corresponding character. Secondly and provided _string2_ <= _string1_ , each character of _string1_ is compared with the corresponding character of _string3_ to ensure that, for each character, _string1_ <= _string3_ . If _both_ conditions are true, that is _string2_ <= _string1_ and _string1_ <= _string3_ are both satisfied, the function returns true, otherwise it returns false. 

## **Example** 

```
Calculate lStatus as chk('b',' ','c')
```

```
# returns true because b>' ' and b<c
```

```
Calculate lStatus as chk('B','B','C')
```

```
# returns true because B=B and B<C
```

```
Calculate lStatus as chk('SD04','AA00','ZZ99')
```

```
# returns true, since for each character of the respective strings,
```

```
# it is true that SD04>AA00 and SD04<ZZ99
```

26 



```
# that is, S>=A, D>=A, 0>=0, 4>=0
```

```
# and S<=Z, D<=Z, 0<=9, 4<=9
```

```
Calculate lStatus as chk('SDA4','AA00','ZZ99')
```

```
# returns false, since in comparing the strings,
```

```
# SDA4 and ZZ99, the character A>9
```

```
Calculate lStatus as (chk('SDA4','AA00','ZZ99')+1=0+1)
```

```
# returns true
```

## **chr()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_String_|NO|All|



## **Syntax** 

**chr** (asciicode1[,asciicode2]…) 

## **Description** 

Returns a string formed by concatenating the supplied ASCII character codes. 

Any argument with a value less than zero or greater than 255 is ignored. 

Only normal printable characters should be stored in Character or National fields. Also, since Omnis uses the character with ASCII value 0 as the end of string marker, this means that if you use this character in any other way, the part of the string following the 0 value is ignored. Control characters in the data file may also cause problems when trying to import or export data. Records with index fields which contain characters with ASCII value 255 may not have the correct index order. It is safe, however, to have unprintable characters in the text for the Transmit text commands. 

## **Example** 

```
Calculate lResult as chr(66,111,111,107)
```

```
# returns 'Book'
```

```
Calculate lResult as chr(257,-1,66,111,111,107)
```

```
# returns 'Book', the first two parameters are ignored
```

## **cmd()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|YES|All|



## **Syntax** 

**cmd** () 

## **Description** 

Returns true if the Cmd key (macOS) or Control key (other platforms) is being pressed. 

27 



**cmp()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Financial_|NO|All|



## **Syntax** 

**cmp** (rate,periods) 

## **Description** 

Returns the compound interest multiplier for a given interest _rate_ over a given number of _periods_ . 

That is, _cmp()_ evaluates the expression (1+( _rate_ /100)) _periods_ ; the interest rate is given by the argument _rate_ /100. 

## **Example** 

```
Calculate lAmount as cmp(10,10) ## = (1+(10/100))10
# returns 2.59 (to 2 decimal places)
```

```
Calculate lAmount as cmp(15,25) ## = (1+(15/100))25
# returns 32.92 (to 2 decimal places)
```

```
Calculate lAmount as cmp(5,0.5) ## = (1+(5/100))0.5
# returns 1.02 (to 2 decimal places)
```

## **cnubintolist()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_List_|NO|All|



## **Syntax** 

**cnubintolist** ( _binary_ ) 

## **Description** 

Returns the list created by converting _binary_ to a list, where _binary_ was created in non-Unicode Studio by assigning a list to a binary variable. 

## **Example** 

```
# Assign a list to a binary variable created in a non-Unicode Studio
Calculate lBinary as lOldList
```

```
# Converts a binary variable to a list in a Unicode Studio
Calculate lNewList as cnubintolist(lBinary)
```

## **complementarycolor()** 

28 



|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|NO|All|



## **Syntax** 

**complementarycolor** ( _color_ ) 

## **Description** 

Returns the complementary color given the passed _color_ value. A complementary color is a color on the opposite side of the color wheel. 

## **compress()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Compression_|NO|All|



## **Syntax** 

**compress** ( _binary_ ) 

## **Description** 

Compresses the data stored in the specified _binary_ variable and returns the binary compressed data. 

It uses the ZLIB compression algorithm to compress the binary variable. To uncompress the result, and return the original uncompressed value, use _uncompress()_ . 

## **Example** 

```
Calculate lCompressed as compress(lOriginal)
```

## **con()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_String_|YES|All|



## **Syntax** 

**con** (string1,string2[,string3]…) 

## **Description** 

Returns a string by concatenating two or more _string_ values. 

**con()** has a limit of 100 parameters. You can exceed this limit by using Calculate _CVAR1 as con(CVAR2,CVAR3)_ where CVAR2 has 99 items and CVAR3 has 99 items, and so on. 

29 



## **Example** 

```
Calculate lFirstName as 'Dick'
Calculate lLastName as 'Rawkins'
Calculate lName as con(lFirstName,' ',lLastName)
# returns 'Dick Rawkins'
```

```
Calculate lResult as con('Omnis',' library')
# returns 'Omnis library'
```

```
Calculate lResult as con('May ',8,'th 200',3)
# returns 'May 8th 2003'
```

```
# Note the use of spaces in the above examples
```

## **contains()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_String_|YES|All|



## **Syntax** 

**contains** ( _string_ , _substring[,ignorecase=kFalse]_ ) 

## **Description** 

Returns true if the _string_ contains the non-empty string _substring_ . If _ignorecase_ is kTrue, the function uses case-insensitive comparison. 

## **Example** 

```
Calculate lString as 'Build better software faster'
```

```
If con(lString,'software')
# returned True
End If
Calculate lBoolean as contains(lString,'SOFTWARE',kTrue)
# lBoolean = True
```

## **cos()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Trigonometric_|YES|All|



## **Syntax** 

**cos** ( _angle_ ) 

## **Description** 

Returns the Cosine of an _angle_ where the _angle_ is in degrees (or radians if #RAD is true). 

30 



**Example** 

```
Calculate lResult as cos(60)
# returns 0.5
```

## **ctrl()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|YES|All|



## **Syntax** 

**ctrl** () 

## **Description** 

Returns true if the Control key (Cmd key on macOS) is being pressed. 

## **cundif()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Class_|NO|All|



## **Syntax** 

**cundif** (differences,class) 

## **Description** 

Restores an older version of a _class_ using the list of _differences_ created by _cdif()._ 

The **cundif()** function is used to roll back the changes made to a class after having compared two versions of the same class with _cdif()._ The list of binary _differences_ must be passed to an older version of the same class. 

Note that you can store multiple sets of differences or “revisions” of a class and, at any time, “reconstruct” an earlier version by successively applying **cundif()** against that particular class. 

## **Example** 

```
# having created lDiffList with cdif()...
Calculate lOldClass as cundif(lDiffList,lNewClass)
```

```
If #ERRCODE
OK message (Sound bell ) {[#ERRTEXT]}
```

```
Quit method
```

```
End If
```

```
# now assign the binary field containing the class to a window class
Calculate lVar1 as $windows.window1.$classdata.$assign(lOldClass)
If lVar1=0 ## class in lOldClass is not a valid window
```

```
OK message (Sound bell ) {The assign has failed...}
Quit method
```

```
End If
```

31 



## **dadd()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Date and Time_|YES|All|



## **Syntax** 

**dadd** (datepart,number,date) 

## **Description** 

Adds a _number_ of date parts to _date_ . 

The _datepart_ argument can be a number of days, months, or quarters depending on the constant you use. The _number_ is interpreted as the number of date or time parts or units specified by a _datepart_ constant. The _number_ argument must be an integer when specifying _datepart_ as kYear, kMonth, kWeek, kQuarter, or kCentiSecond (the fractional part of a number is ignored). You can use fractions for the other date parts. 

The datepart constants that you can use are: kYear, kMonth, kWeek, kQuarter, kDay, kHour, kMinute, kSecond, kCentiSecond. 

## **Example** 

```
Calculate lDate as dadd(kDay,3,#D)
```

```
# returns May 11, 2003, that is, 3 days are added, assume #D is May 8, 2003
```

## `Calculate lDate as dadd(kWeek,1.2,#D)` 

```
# returns May 16, 2003, that is, 1 week is added, the fraction is ignored, assume #D is May 8, 2003
```

## **dat()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Date and Time_|YES|All|



## **Syntax** 

**dat** (datestring|number[,dateformat]) 

## **Description** 

Converts a _datestring_ or _number_ to a date value using an optional _dateformat_ string and returns the result. JavaScript client-executed methods do not support _number_ . 

If you do not specify a _dateformat,_ the first argument is converted using #FD. You can use the following symbols in the _dateformat_ string: 

|Y|Year (03)|d|Day (12th)|
|---|---|---|---|
|y|Year (2003)|W|Day of week (5)|
|C|Century (20)|w|Day of week (Friday)|
|M|Month (06)|V|Short day of week (Fri)|
|m|Month (JUN)|E|Day of year (1-366)|
|n|Month (June)|G|Week of year (1-52)|
|D|Day (12)|F|Week of month (1-6)|



32 



## **Example** 

```
Calculate Calculate lDate as dat('May 8th, 03')
# returns '8 MAY 03' if #FD = 'D m Y'
```

```
Calculate lDate as dat('May 8th, 2003','MDY')
# returns 050803
```

```
Calculate lDate as dat(91,'w, d n, y')
# returns 'Monday, 1st April, 1901' i.e. the 91st day of 1901
```

## **ddiff()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Date and Time_|NO|All|



## **Syntax** 

**ddiff** (datepart,date1,date2) 

## **Description** 

Returns the difference between two dates, _date1_ and _date2_ , in the units specified by a _datepart_ constant; the specified dates are included in the evaluation. 

When you specify one of the day of the week constants (kSunday thru kSaturday) as the _datepart_ argument, you get the number of occurrences of that day between the two dates. When you specify kYear,kQuarter, kMonth, or kWeek as the _datepart_ argument, the function counts the end of years, quarters, months, or weeks between the two dates. 

The datepart constants that you can use are: kYear, kMonth, kWeek, kQuarter, kDay, kSunday thru kSaturday, kHour, kMinute, kSecond, kCentiSecond. 

## **Example** 

```
Calculate lDiff as ddiff(kMonth,"1/31/03","3/1/03")
# returns 2
```

```
Calculate lDiff as ddiff(kDay,"4/8/03",#D)
```

```
# returns 30, the number of days between the two dates, assume #D is May 8, 2003
```

## **decstr()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_String_|NO|All|



## **Syntax** 

**decstr** (string[,key,unicode=ktrue]) 

## **Description** 

Decodes _string_ (encoded with _encstr_ ()) using _key_ and returns result. _key_ can be a string of 1-255 characters in length, previously used with encstr(). If omitted, uses the default _key_ . If _unicode_ false and _string_ not marked as Unicode, string must have been encoded by non-Unicode Omnis. 

Note that decstr(encstr(string,key),key) = string. 

33 



## **Example** 

```
Calculate lEncoded as encstr('Testing',10)
Calculate lDecoded as decstr(lEncoded,10)
# returns the original string 'Testing'
```

## **decxtea()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Binary Field_|NO|All|



## **Syntax** 

**decxtea** (binary,key) 

## **Description** 

Returns the binary result of decrypting _binary_ (previously encoded using _encxtea_ ()) with the binary _key_ ; the _key_ must be 128 bits long. 

## **delchars()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_String_|YES|All|



## **Syntax** 

**delchars** ( _string_ , _position_ [, _length_ =1]) 

## **Description** 

Returns the string generated by deleting the substring at the specified 1-based _position_ and _length_ from _string_ . If length extends past the end of the string it just deletes to the end. 

## **Example** 

```
Calculate lString as delchars('String',2,2)
# lString is now ‘Sing’
```

## **dim()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Date and Time_|YES|All|



## **Syntax** 

**dim** (datestring,number) 

## **Description** 

Increments a _datestring_ by a _number_ of months and returns the result. 

Months containing different numbers of days are accounted for. For example, Jan 31 96 increased by one month gives Feb 29 96, but beware, Feb 29 96 decreased by one month (using a negative value) gives Jan 29 96, not Jan 31 96. 

34 



## **Example** 

```
Calculate lDate as dim(dat('5/8/03'),15)
# returns 'AUG 8 04', if #FD = 'm D Y'
```

```
Calculate lDate as dim(dat('5/8/03'),-1)
# returns 'APR 8 03', if #FD = 'm D Y'
```

## **dname()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Date and Time_|NO|All|



## **Syntax** 

**dname** (datepart,date) 

## **Description** 

Returns the name of the day or month of a specified _date_ , depending on a _datepart_ constant which can be either kMonth or kDay. 

## **Example** 

```
Calculate lDate as dname(kMonth,#D)
# returns May, assumes #D is May 8, 2003
```

## **DNet.$addclass()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_DNet_|NO|All|



## **Syntax** 

**DNet.$addclass** ( _FileName_ ) 

## **Description** 

Loads classes from _FileName_ (or FileNames if comma-separated). 

## **DNet.$basefolder()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_DNet_|NO|All|



## **Syntax** 

**DNet.$basefolder** () 

## **Description** 

Returns the base folder of the .NET classes. 

35 



## **DNet.$getenum()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_DNet_|NO|All|



## **Syntax** 

## **DNet.$getenum** ( _EnumName_ ) 

## **Description** 

Returns the value of the fully qualified specified enum (e.g. System.IO.FileMode.Open). 

## **dpart()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|upto 35990_Date and Time_|NO|All|
|asof 35991_Date and Time_|YES|All|



## **Syntax** 

**dpart** (datepart,date) 

## **Description** 

Returns a number that represents a part of the specified _date_ depending on the _datepart_ constant used. 

This is useful when you want to know the week number (that is, the week of the year; use kWeek), the day of the year or the day of the week, and so on. 

The datepart constants that you can use are: kYear, kMonth, kWeek, kDayofYear, kQuarter, kMonthofQuarter, kWeekofQuarter, kDayofQuarter, kWeekofMonth, kDay, kDayofWeek, kHour, kMinute,kSecond, kCentiSecond. 

When this function returns the week of the year (kWeek) the calculation is based on 1 Jan being the first day of the first week of the year, the last day of the year is week 53. 

dpart(kDayofWeek,date) assumes Sunday is day 1. 

## **Example** 

## `Calculate lDate as dpart(kWeek,#D)` 

```
# returns 19, the week number, when #D is May 8, 2003
```

```
Calculate lDate as dpart(kMonth,#D)
```

```
# returns 5, the month number, when #D is May 8, 2003
```

## **dtcy()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Date and Time_|YES|All|



## **Syntax** 

**dtcy** (datestring) 

36 



## **Description** 

Returns the year and century of a _datestring_ as a string. 

## **Example** 

```
Calculate lDate as dtcy(#D)
# returns '2003', assume #D is May 8, 2003
```

```
Calculate lDate as dtcy('05 08 03')
# returns '2003', assume #D is May 8, 2003
```

## **dtd()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Date and Time_|YES|All|



## **Syntax** 

**dtd** (datestring[,jsnumber=kfalse]) 

## **Description** 

Returns the day part of a _datestring_ . For JavaScript client-executed code, _jsnumber_ kTrue returns a number rather than a string; in all other cases returns a string unless it is part of a calculation. 

## **Example** 

```
Calculate lDate as dtd(dat('May 8 03'))
# returns '8th'
```

```
Calculate lDate as con(dtd(dat ('May 8 03')),' day')
# returns '8th day'
```

```
Calculate lDate as dtd(dat('May 8 03'))+20
# returns 28
```

## **dtm()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Date and Time_|YES|All|



## **Syntax** 

**dtm** (datestring[,jsnumber=kfalse]) 

## **Description** 

Returns the month part of a _datestring_ . For JavaScript client-executed code, _jsnumber_ kTrue returns a number rather than a string; in all other cases returns a string unless it is part of a calculation. 

37 



## **Example** 

```
Calculate lDate as dtm(dat('May 8 2003'))
# returns 'May'
```

```
Calculate lDate as dtm(dat('May 8 03'))+20
# returns 25
```

```
Calculate lDate as dtm(dat(dat('May 8 03')+30))
# returns 'June'
```

## **dtw()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Date and Time_|YES|All|



## **Syntax** 

**dtw** (datestring[,jsnumber=kfalse]) 

## **Description** 

Returns the day of the week of a _datestring_ . For JavaScript client-executed code, _jsnumber_ kTrue returns a number rather than a string; in all other cases returns a string unless it is part of a calculation. dtw() assumes Monday is day 1. 

## **Example** 

```
Calculate lDate as dtw(dat('May 8 1977'))
# returns 'Sunday'
Calculate lDate as dtw(dat('May 8 03'))+20
# returns 24
```

```
Calculate lDate as dtw(dat(dat('May 8 03')+20))
# returns 'Wednesday'
```

## **dty()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Date and Time_|YES|All|



## **Syntax** 

**dty** (datestring[,jsnumber=kfalse]) 

## **Description** 

Returns the year part of a _datestring_ . For JavaScript client-executed code, _jsnumber_ kTrue returns a number rather than a string; in all other cases returns a string unless it is part of a calculation. 

The string representation of the year part of a date is the set of numeric characters representing the year, that is, 00, 01, 02, 03, and so on, while the numeric representation is the number of years since the start of the century. 

38 



## **Example** 

```
Calculate lDate as dty(dat('8 May 03'))
# returns '03'
```

```
Calculate lDate as dty(dat('May 8 03'))+20
# returns 23
```

## **encstr()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_String_|NO|All|



## **Syntax** 

**encstr** (string[,key]) 

## **Description** 

Encodes the _string_ using _key_ and returns the result. _key_ can be a string of 1-255 characters in length. If omitted, Omnis uses the default _key_ . encstr() marks the string to indicate that it was encoded using Unicode Omnis. 

The return value of **encstr()** is a string that is difficult to decode without knowing the key. To decode the string, and return the original value, use the function _decstr(_ ) _._ 

## **Example** 

```
Calculate lEncoded as encstr('Testing',10)
# encodes the string 'Testing' with the key 10
```

## **encxtea()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Binary Field_|NO|All|



## **Syntax** 

**encxtea** (binary,key) 

## **Description** 

Returns the binary result of encrypting _binary_ using the eXtended Tiny Encryption Algorithm (XTEA) with the binary _key_ ; the _key_ must be 128 bits long. 

## **endswith()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_String_|YES|All|



## **Syntax** 

**endswith** ( _string_ , _end[,ignorecase=kFalse]_ ) 

39 



## **Description** 

Returns true if the _string_ ends with the non-empty string _end_ . If _ignorecase_ is kTrue, the function uses case-insensitive comparison. 

## **Example** 

```
Calculate lString as 'One Code'
If endswith(lString,'Code')
# returned True
End If
```

```
Calculate lBoolean as endswith(lString,'CODE',kTrue)
# lBoolean = True
```

## **errcode()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|YES|All|



**Syntax errcode** () **Description** Returns #ERRCODE. 

## **errtext()** 

|**Syntax**<br>**errtext**()<br>**Description**<br>Returns #ERRTEXT.|Function group<br>Execute on client<br>Platform(s)|
|---|---|
||_General_<br>YES<br>All|
|||



## **eval()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|NO|All|
|**Syntax**|||



**eval** ( _string_ ) 

40 



## **Description** 

Evaluates a calculation expressed as a character string and returns the result. 

For example, if _lVar2_ contains the string ‘3*4/2’, _eval(lVar2_ ) returns the result 6. You should use this function with extreme care because a runtime error will occur if the string is not a valid calculation. You can use the Test for valid calculation command to test a string before attempting to evaluate it. 

## **Example** 

```
Calculate lVar2 as '3*lVar1/15.5'
Test for valid calculation {eval(lVar2)}
If flag true
Calculate lTax as eval(lVar2)
End If
```

## **evalf()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|NO|All|



## **Syntax** 

**evalf** (fieldname|variable) 

## **Description** 

Evaluates a calculation passed as a string in a character or binary _variable_ and returns the result. If _variable_ is of type binary, evalf() returns the tokenized calculation in _variable_ for faster execution of subsequent calls. 

The function **evalf()** is faster than the equivalent _eval()_ ; you should use it when your code will repeat an evaluation several times. You should use it in the _Set search as calculation_ command and as the calculation for a window list field. 

**evalf()** takes a single argument that must be a _fieldname_ or _variable_ . If the contents of this field or variable is the text for a valid calculation, **evalf()** returns the result of the calculation, else a runtime error occurs. At the same time, the tokenized form of the calculation is stored back in the field or variable, so that next time **evalf()** is called, there is no need to tokenize or check the string. Tokenizing a string is part of the interpretation process; once done, Omnis can evaluate the calculation quickly. If you change the contents of the field or variable **evalf()** uses, Omnis will recognize that the new string requires checking and tokenizing. 

## **Example** 

```
Test for valid calculation {evalf(lSearch)}
If flag true
```

```
Set search as calculation {evalf(lSearch)}
End If
```

```
Find first on lTown (Use search)
```

```
Calculate lVar1 as 'lTax*100'
Calculate lTotal as lVar2+evalf(lVar1)
```

## **exp()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Logarithmic_|YES|All|



41 



## **Syntax** 

**exp** (number) 

## **Description** 

Returns e raised to the power of a given _number_ , or 1e100 on overflow. 

## **Example** 

```
Calculate lResult as exp(0.5)
# returns 1.6487
```

## **fact()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Number_|NO|All|



## **Syntax** 

**fact** ( _number_ ) 

## **Description** 

Returns the factorial of a _number_ rounded to an integer first. If _number_ <= 0, 1 is returned, and if _number_ >= 70, 1e100 is returned. 

## **Example** 

```
Calculate lResult as fact(4)
# returns 24, that is 4*3*2*1
```

## **fday()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Date and Time_|NO|All|



## **Syntax** 

**fday** (datepart,date) 

## **Description** 

Returns the date of the first day of the year, month, week or quarter in which the specified _date_ falls. 

The period is specified using one of the following _datepart_ constants: kYear, kQuarter, kMonth, kWeek. 

## **Example** 

```
Calculate lDate as fday(kWeek,#D)
```

```
# returns May 4, 2003 if the start of the week is set to Sunday
```

```
Calculate lDate as fday(kQuarter,#D)
```

```
# returns April 1 2003, that is, the first day of the quarter in which today falls, #D is May 8, 2003
```

42 



## **FileOps.$changeworkingdir()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_FileOps_|NO|All|



## **Syntax** 

## **FileOps.$changeworkingdir** ( _cPath_ ) 

## **Description** 

Changes the current working directory to the directory named in _cPath_ . Pathnames can be over 255 characters, which was the limit in Studio 8.0.1 or earlier. 

**$changeworkingdir()** only switches between directories on the same drive, not between drives. The function returns an error code, or zero if successful: see the _FileOps function error codes_ . 

Note: Applications on macOS do not have a working directory. If you use this function on macOS, it returns the error code kFileOpsNoOperation. 

## **Example** 

```
Switch platform()
Case 'X' ## for macOS
Quit method ;; working directories not supported
Case 'U' ## for Linux
Do FileOps.$changeworkingdir('/omnis/examples') Returns lError
Default ## for Windows platforms
Do FileOps.$changeworkingdir('c:\omnis\examples') Returns lError
```

```
End Switch
```

```
OK message {Working directory is now: [FileOps.$getworkingdir()]}
```

## **FileOps.$converthfspathtoposixpath()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_FileOps_|NO|macOS|



## **Syntax** 

## **FileOps.$converthfspathtoposixpath** ( _cHfsPath,&cPosixPath_ ) 

## **Description** 

Converts an HFS file path to a POSIX file path. Pathnames can be over 255 characters, which was the limit in Studio 8.0.1 or earlier. 

An HFS file path is colon-delimited, where a leading colon indicates a relative path, otherwise the first component denotes the volume. A POSIX path is slash-delimited. 

On any other platform, other than macOS, **$converthfspathtoposixpath()** simply copies _cHfsPath_ to _cPosixPath._ 

## **Example** 

```
Do FileOps.$converthfspathtoposixpath(":Applications:Calculator",lPosixPath)
# lPosixPath is returned as "Applications/Calculator"
```

43 



**FileOps.$convertposixpathtohfspath()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_FileOps_|NO|macOS|



## **Syntax** 

## **FileOps.$convertposixpathtohfspath** ( _cPosixPath,&cHfsPath_ ) 

## **Description** 

Converts a POSIX file path to an HFS file path. Pathnames can be over 255 characters, which was the limit in Studio 8.0.1 or earlier. 

An HFS file path is colon-delimited, where a leading colon indicates a relative path, otherwise the first component denotes the volume. A POSIX path is slash-delimited. 

On any other platform, other than macOS, **$convertposixpathtohfspath()** simply copies _cPosixPath_ to _cHfsPath._ 

## **Example** 

```
Do FileOps.$convertposixpathtohfspath("Applications/Calculator",lHfsPath)
# lHfsPath is returned as ":Applications:Calculator"
```

## **FileOps.$copyfile()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_FileOps_|NO|All|



## **Syntax** 

**FileOps.$copyfile** ( _cFromPath,cToPath_ ) 

## **Description** 

Copies the file specified in _cFromPath_ to the file _cToPath_ . The file named in _cToPath_ must not already exist. Pathnames can be over 255 characters, which was the limit in Studio 8.0.1 or earlier. 

_cToPath_ is the path to destination folder into which the file will be copied; the file to be copied must not already exist in the destination folder. 

The function returns an error code, or zero if successful: see the _FileOps function error codes_ . 

To move a file, rather than copy it, use _$movefile()_ . 

## **Example** 

```
Do FileOps.$copyfile('c:\omnis\test.txt','c:\examples\test.txt') Returns lError
# copies 'test.txt' to the 'examples' folder
```

```
Do FileOps.$copyfile('c:\omnis\test.txt','c:\examples\test2.txt') Returns lError
# copies 'test.txt' to 'test2.txt' in the 'examples' folder
```

```
Do FileOps.$copyfile('c:\omnis\test.txt','c:\omnis\test2.txt') Returns lError
# copies 'test.txt' to 'test2.txt' in the same folder
```

## **FileOps.$createdir()** 

44 



|Function group|Execute on client|Platform(s)|
|---|---|---|
|_FileOps_|NO|All|



## **Syntax** 

**FileOps.$createdir** ( _cPath_ [,bCreateParentDirs=kFalse]) 

## **Description** 

Creates a directory with the pathname _cPath_ . Pathnames can be over 255 characters, which was the limit in Studio 8.0.1 or earlier. 

With the exception of the last directory, all directories specified in the _cPath_ parameter must already be present, unless bCreateParentDirs is kTrue, in which case any parent directories in cPath that do not exist are also created. 

If bCreateParentDirs is kTrue and the directory in cPath already exists, FileOps will return 0 (success) rather than 101215 (A file with the specified name already exists). If bCreateParentDirs is kFalse (default), or is omitted, then the usual 101215 is returned if directory in cPath already exists. 

The function returns an error code, or zero if successful: see the _FileOps function error codes_ . 

## **Example** 

```
Do FileOps.$createdir('c:\omnis\examples\extcomp\clock') Returns lError
```

```
# creates the 'clock' folder assuming c:\omnis\examples\extcomp is a valid path
```

## **FileOps.$deletefile()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_FileOps_|NO|All|



## **Syntax** 

**FileOps.$deletefile** ( _cPath_ [deleteContents=kFalse,recursive=kFalse]) 

## **Description** 

Deletes the file or folder named _cPath_ . Pathnames can be over 255 characters. The optional parameters deleteContents and recursive allow you to delete the contents of a folder (both default to kFalse, if omitted). 

Files deleted with **$deletefile()** are not moved into the Recycled bin or Trash can, _they are deleted irreversibly._ You can delete a folder with **$deletefile()** , but only if it is empty. 

The combination of the parameters has the following results: 

- FileOps.$deletefile(cPath, kFalse, kFalse) 

- (same as if deleteContents and recursive are omitted) if cPath is a folder, the folder will be deleted only if empty, that if no files or directories are present in the folder. On macOS, the function checks if the only file is .DS_Store and will delete the folder in that case. If there are hidden files in the folder, the folder and the hidden files will not be deleted. 

- FileOps.$deletefile(cPath, [kTrue, kFalse]) 

- if cPath is a folder, _all files_ inside the folder if deleteContents is true, but any subfolders _will not_ be deleted. Furthermore, if the folder is empty, the folder will not be deleted. 

- FileOps.$deletefile(cPath, kFalse, kTrue) 

- if cPath is a folder, it will be deleted only if empty. If there are any contents, those will not be deleted as deleteContents is kFalse, even if recursive is kTrue. 

- FileOps.$deletefile(cPath, kTrue, kTrue) 

if cPath is a folder, it will be wiped off the disk with its contents, if any are present. 

45 



- FileOps.$deletefile(cFilePath) 

if cPath is a file, the file will be removed regardless of the deleteContents or recursive values - the deleteContents and recursive parameters do not impact the behavior of deleting files, only the behavior of deleting folders. 

The function returns an error code, or zero if successful: see the _FileOps function error codes_ . 

## **Example** 

```
Do FileOps.$deletefile('c:\omnis\examples\extcomp\test1.txt') Returns lError
```

```
# deletes 'test1.txt' from 'c:\omnis\examples\extcomp'
```

```
Do FileOps.$changeworkingdir('c:\omnis') Returns lError
```

```
Do FileOps.$deletefile('test2.txt') Returns lError
```

```
# deletes 'test2.txt' at the current folder 'c:\omnis'
```

```
Do FileOps.$deletefile('c:\omnis\examples\extcomp\clock') Returns lError
```

```
# deletes the 'clock' folder if empty
```

## **FileOps.$doesfileexist()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_FileOps_|NO|All|



## **Syntax** 

## **FileOps.$doesfileexist** ( _cPath_ ) 

## **Description** 

Returns true if the file or folder named _cPath_ exists. Otherwise, it returns false. Pathnames can be over 255 characters, which was the limit in Studio 8.0.1 or earlier. 

## **Example** 

```
Switch platform()
```

```
Case 'X' ## for macOS
```

```
Do FileOps.$doesfileexist('/Omnis/Tutorial/mylibs.lbs') Returns lStatus
```

```
Case 'U' ## for Linux
```

```
Do FileOps.$doesfileexist('/omnis/tutorial/mylib.lbs') Returns lStatus
```

- `Default ## for Windows` 

```
Do FileOps.$doesfileexist('c:\omnis\tutorial\mylibs.lbs') Returns lStatus
```

```
End Switch
```

```
# lStatus is true if 'mylib.lbs' exists in the Omnis tutorial
```

## **FileOps.$filelist()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_FileOps_|NO|All|



## **Syntax** 

**FileOps.$filelist** (iInclude,cPath[,iInformation,cFilter,&cErrorText]) 

46 



## **Description** 

Returns a list of files, directories, and volumes at the location specified in _cPath_ . Errors are reported to _cErrorText_ . Pathnames can be over 255 characters, which was the limit in Studio 8.0.1 or earlier. 

The parameter iInclude specifies what to include in the list using a combination of the constants kFileOpsIncludeFiles, kFileOpsIncludeDirectories, and kFileOpsIncludeVolumes. Use + to combine the constants. 

If you use kFileOpsIncludeVolumes, then the function adds a line for each volume to the start of the list. The remaining lines in the list, or all lines if you do not use kFileOpsIncludeVolumes, comprise a line for each file or directory in the directory cPath. You can restrict the files returned in the list using the optional filter cFilter. Note that cFilter does not apply to volume or directory names. The filter is a semicolon separated list of file-matching specifications. On all platforms, a file-matching specification can have the form *.<ext>, to match all files with the extension <ext>, or *.* to match all files. On macOS, a file-matching specification can also have the form ‘TYPE’ , ‘TYPE,CREATOR’, or ‘,CREATOR’, where TYPE and CREATOR are the 4 character, case-sensitive Mac file type and creator. Note that in this case, the single quotes are part of the file-matching specification. Example file-matching specifications: 

*.txt Matches files with .txt as their extension 

- *.txt;*.lbs Matches files with .txt or .lbs as their extension 

- “TEXT”;“,OO$$”;*.txt Matches files of type TEXT, or created by Omnis Studio, or with .txt as their extension. 

- “OO$A,OO$$” Matches Omnis libraries used under macOS. 

You specify the information to be returned by passing information as a combination of the kFileOpsInfo… constants listed in the following table. If you omit iInformation, only the name is returned. The returned list contains a column for each kFileOpsInfo… constant you specify. The columns you specify occur in the same order as the table. 

|Col name|information constant|description|
|---|---|---|
|name|kFileOpsInfoName|name of the fle|
|name83|kFileOpsInfoName83|DOS 8.3 name of the fle|
|fullname|kFileOpsInfoFullName|full pathname of the fle|
|readonly|kFileOpsInfoReadOnly|fle’s read-only status|
|hidden|kFileOpsInfoHidden|fle’s hidden status (* see below)|
|size|kFileOpsInfoSize|logical size of fle|
|actualsize|kFileOpsInfoActualSize|physical size of fle on disk; same as logical size under Windows|
|created|kFileOpsInfoCreated|date and time the fle was created|
|modifed|kFileOpsInfoModifed|date and time the fle was modifed|
|creator|kFileOpsInfoCreatorCode|the fle’s creator under macOS, blank under Windows|
|type|kFileOpsInfoTypeCode|the fle’s type under macOS, the fle extension under Windows|



* On Linux, filenames beginning with “.” (hidden files) are not identified as hidden. 

The function returns an empty list if an error occurs. The FileOps object supports 64-bit integers for file sizes and for offsets, etc in files. 

## **Example** 

```
Do FileOps.$filelist(kFileOpsIncludeFiles+kFileOpsIncludeDirectories,sys(115)) Returns lFileList
# returns a list of files and directories in the main Omnis folder
```

## `Do FileOps.$filelist(` 

```
# returns a list of DLLs in the Omnis\External folder including the name, size, creation date and time of each
```

## `Do FileOps.$filelist(` 

## **FileOps.$getfileinfo()** 

47 



|Function group|Execute on client|Platform(s)|
|---|---|---|
|_FileOps_|NO|All|



## **Syntax** 

**FileOps.$getfileinfo** ( _cPath,iInformation_ ) 

## **Description** 

Returns a list of file information for the file named _cPath_ . Pathnames can be over 255 characters, which was the limit in Studio 8.0.1 or earlier. 

You specify the information to be returned by passing iInfoFlags as a combination of the kFileOpsInfo… constants listed in the following table. If you omit iInfoFlags, only the name is returned. The returned list contains a column for each kFileOpsInfo… constant you specify. The columns you specify occur in the same order as the table. 

|Col name|info fags constant|description|
|---|---|---|
|name|kFileOpsInfoName|name of the fle|
|name83|kFileOpsInfoName83|DOS 8.3 name of the fle|
|fullname|kFileOpsInfoFullName|full pathname of the fle|
|readonly|kFileOpsInfoReadOnly|fle’s read-only status|
|hidden|kFileOpsInfoHidden|fle’s hidden status|
|size|kFileOpsInfoSize|logical size of fle|
|actualsize|kFileOpsInfoActualSize|physical size of fle on disk; same as logical size under Windows and Unix|
|created|kFileOpsInfoCreated|date and time the fle was created|
|modifed|kFileOpsInfoModifed|date and time the fle was modifed|
|creator|kFileOpsInfoCreatorCode|the fle’s creator under macOS, blank under Windows and Unix|
|type|kFileOpsInfoTypeCode|the fle’s type under macOS, the fle extension under Windows and Unix|
|linkedname|kFileOpsInfoLinkedName|macOS: the path of the linked fle (if any)Windows: the path of the shortcut target (if any)Unix: the path of the symbolic link target|
|||(if any)|
|isdirectory|kFileOpsInfoIsDirectory|if the path specifed points to a directory|
|calcdirectorysize|kFileOpsInfoCalcDirectorySize|the size in bytes of the directory on the fle system|



The function returns an empty list if an error occurs. The FileOps object supports 64-bit integers for file sizes and for offsets, etc in files. 

## **Example** 

```
Do sys(10) Returns lPath
# returns the name and path of the current library
```

```
Do FileOps.$getfileinfo(lPath,kFileOpsInfoName+kFileOpsInfoSize+kFileOpsInfoCreated) Returns lFileList
# returns the name, size, creation date and time of the current library
```

```
Do lFileList.$redefine(lFilename,lSize,lCreated)
Do lst(lFileList,1,lSize) Returns lSize
# returns the value in the size column
```

## **FileOps.$getfilename()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_FileOps_|NO|All|



## **Syntax** 

**FileOps.$getfilename** (&cPath[,cPrompt,cFilter,cInitialDirectory,iAppflags]) 

48 



## **Description** 

Opens the standard Open file dialog. 

You can specify the dialog title in _cPrompt_ , and restrict the files displayed using a filter passed in _cFilter_ . The filter comprises one or more entries separated by the vertical bar character ‘|’. Each filter entry has two components, again separated by a vertical bar. The filter entries populate the file-type selection dropdown or popup list. The first component of an entry is the text to display in the dropdown or popup list. The second component is a file-matching specification. On all platforms, a file-matching specification can have the form *.<ext>, to match all files with the extension <ext>, or *.* to match all files. On macOS, a file-matching specification can also have the form TYPE or TYPE,CREATOR, where TYPE and CREATOR are the 4 character, case-sensitive Mac file type and creator. Example _cFilter_ parameters: 

|Text fles|*.txt|
|---|---|
|Text fles|*.txt|



You can also specify the initial directory for the Open dialog in _cInitialDirectory_ . 

The _iAppflags_ parameter only applies when running on macOS. It is optional; if specified, it must be a combination of the following constants: 

|kFileOpsSelectApps|Allows applications to be selectable within the dialog|
|---|---|
|kFileOpsOpenApps|Allows the dialog to browse the content of applications|



Note that kFileOpsOpenApps automatically implies kFileOpsSelectApps, although it is valid to specify both flags (kFileOpsSelectApps + kFileOpsOpenApps). 

The name and full path of the file selected by the user is returned in the _cPath_ parameter. Note that the file is not open: you must do something with the file name and path returned. Pathnames can be over 255 characters, which was the limit in Studio 8.0.1 or earlier. 

Note that if the file selected is an alias/shortcut/link, then the returned value is the result of resolving the alias/shortcut/link to its target, not the path of the alias/shortcut/link. 

**$getfilename()** returns true if the user selected a file and pressed OK. Otherwise, it returns false, meaning that the user pressed Cancel. 

## **Example** 

```
# returns the name and full path of the file selected, e.g. 'c:\omnis\help\omnis\omnis.ohf'
```

## **FileOps.$getlasterror()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_FileOps_|NO|All|



## **Syntax** 

## **FileOps.$getlasterror(** [&cErrorText]) 

## **Description** 

Returns any errors in _cErrorText_ from the last FileOps method that was executed. 

Returns the error code from the last FileOps method executed; also optionally populates cErrorText with a description of the error. If no error occurred, the method returns zero and the error text is empty. 

49 



## **FileOps.$getunixpermissions()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_FileOps_|NO|Linux, macOS|



## **Syntax** 

## **FileOps.$getunixpermissions** ( _cPath_ ) 

## **Description** 

Returns the Unix permissions string for the file identified by _cPath_ . Pathnames can be over 255 characters, which was the limit in Studio 8.0.1 or earlier. 

If an error occurs, it returns an empty string. If it succeeds, then it returns the standard 10 character Unix file permissions string for the file. The first character is either d for a directory, or - for a file. The remaining 9 characters are split into three groups of three characters. The groups are for the user categories owner, group and other, in that order. The characters within each group have the following meanings: 

|Character index|Value|
|---|---|
|1|r means that members of the user category can read the fle; - means they cannot.|
|2|w means that members of the user category can write to the fle; - means they cannot.|
|3|x means that members of the user category can execute the fle; - means they cannot.|



## **Example** 

```
Do FileOps.$getunixpermissions('/omnis/myfile') Returns lPermissions
```

```
# returns '-rwxr-xr-x' meaning that the file is only writable by its owner, and readable and executable by all
```

## **FileOps.$getworkingdir()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_FileOps_|NO|Windows|



## **Syntax** 

## **FileOps.$getworkingdir** () 

## **Description** 

Returns the current working directory (no parameters required), so is only useful when running in Windows. The function returns an empty string if an error occurs. 

Note: Applications on macOS do not have a working directory. If you use this function on macOS, it returns an empty string. 

## **Example** 

```
Do FileOps.$changeworkingdir(sys(115)) Returns lError
Do FileOps.$getworkingdir() Returns lWorkDir
```

## **FileOps.$movefile()** 

50 



|Function group|Execute on client|Platform(s)|
|---|---|---|
|_FileOps_|NO|All|



## **Syntax** 

**FileOps.$movefile** ( _cFromPath,cToPath_ ) 

## **Description** 

Moves the file _cFromPath_ to the new location _cToPath_ . Pathnames can be over 255 characters, which was the limit in Studio 8.0.1 or earlier. 

_cFromPath_ is the pathname of the file to be moved. _cToPath_ is the pathname of the destination folder into which the file will be moved (if you include a file name in _cToPath_ the function will fail under macOS); the file to be moved must not already exist in the destination folder. The function returns an error code, or zero if successful: see the _FileOps function error codes_ . 

To copy a file, rather than move it, use _$copyfile()_ . 

Note that **$movefile()** cannot move a file across volumes. Use _$copyfile()_ and _$deletefile()_ instead. 

## **Example** 

## `Do FileOps.$movefile(` 

```
'c:\omnis\examples\extcomp\extcomp.lbs','c:\omnis\startup\extcomp.lbs') Returns lError
# moves the library 'extcomp.lbs' to the Omnis\Startup folder
```

## **FileOps.$parentdir()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_FileOps_|NO|All|



## **Syntax** 

**FileOps.$parentdir** ( _cPath_ ) 

## **Description** 

Returns the pathname of the directory containing the file or directory identified by cPath, i.e. its parent directory. Pathnames can be over 255 characters, which was the limit in Studio 8.0.1 or earlier. 

## **FileOps.$putfilename()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_FileOps_|NO|All|



## **Syntax** 

**FileOps.$putfilename** (&cPath[,cPrompt,cFilter,cInitialDirectory,iAppflags]) 

51 



## **Description** 

Opens the standard Save file dialog. 

You can supply a default value for the file name in _cPath_ . Pathnames can be over 255 characters, which was the limit in Studio 8.0.1 or earlier. 

You can specify the dialog title in _cPrompt_ . 

You can use _cFilter_ on Windows and Linux in a similar way to the _cFilter_ parameter of _$getfilename()_ . 

You can also specify the initial directory for the Save dialog in _cInitialDirectory_ . 

The _iAppflags_ parameter is a combination of the following constants: 

|kFileOpsSelectApps|If passed allows applications to be selectable within the dialog (macOS only)|
|---|---|
|kFileOpsOpenApps|If passed allows the dialog to browse the content of applications (macOS only)|
|kFileOpsWindowsDisablePrompt|If passed the fle already exists prompt is disabled: see below* (Windows only)|



Note that kFileOpsOpenApps automatically implies kFileOpsSelectApps, although it is valid to specify both flags (kFileOpsSelectApps + kFileOpsOpenApps). 

*Studio 11 or above: When running on Windows, the dialog opened by FileOps.$putfilename() now prompts if the file already exists, unless kFileOpsWindowsDisablePrompt is passed in the iAppFlags parameter. This makes the default behavior compatible with macOS (the file already exists prompt cannot be disabled on macOS). 

The name and full path of the file entered by the user is returned in _cPath_ . Note that the file is not saved: you must write the code to output the file. **$putfilename()** returns true if the user selected a file and pressed OK. Otherwise, it returns false, meaning that the user pressed Cancel. 

## **Example** 

```
Calculate lPath as 'Default.rep'
# set the default name
```

```
Do FileOps.$putfilename(lPath,'Save print file','*.rep','c:\omnis\examples') Returns lError
```

```
# opens the Save dialog with the title 'Save print file' and returns the name and full path of file entered by
```

## **FileOps.$readfile()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_FileOps_|NO|All|



## **Syntax** 

**FileOps.$readfile** ( _cFilePath,&vVariable_ [, _iEnc_ =kUniTypeAuto]) 

## **Description** 

Reads the file _cFilePath_ into the variable _vVariable_ . Returns an integer error code (zero for success). 

_cFilePath_ (Character 100000000) The pathname of the file. 

_vVariable_ (Variant) The variable into which the file contents will be read. Binary or Character. It it is Character, the file contents are converted to Character using the encoding specified by the iEnc parameter. 

_iEnc_ (Integer 32 bit, default is kUniTypeAuto) The encoding used to convert the file contents to Character. A kUniType… constant, not kUniTypeBinary or kUniTypeCharacter. Only used when _vVariable_ is a Character variable. 

See FileOps.$writefile(). 

52 



## **FileOps.$rename()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_FileOps_|NO|All|



## **Syntax** 

**FileOps.$rename** ( _cOldname,cNewname_ ) 

## **Description** 

Renames the file or folder named _cOldname_ to _cNewname_ . 

The function returns an error code, or zero if successful: see the _FileOps function error codes_ . 

## **Example** 

```
Do FileOps.$rename('c:\omnis\libs','c:\omnis\examples') Returns lError
# renames the 'libs' folder to 'examples'
```

```
Do FileOps.$changeworkingdir('c:\omnis\datafile\odbc') Returns lError
Do FileOps.$rename('odbc.txt','readme.txt') Returns lError
```

```
# switches to the 'c:\omnis\datafile\odbc' folder and renames 'odbc.txt' to 'readme.txt'
```

## **FileOps.$selectdirectory()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_FileOps_|NO|All|



## **Syntax** 

**FileOps.$selectdirectory** (&cPath[,cPrompt,cInitialDirectory,iAppflags]) 

## **Description** 

Opens the Select folder dialog. 

You can specify the dialog title in _cPrompt_ , and the initial directory in _cInitialDirectory_ . 

The _iAppflags_ parameter only applies when running on macOS. It is optional; if specified, it must be a combination of the following constants: 

|kFileOpsSelectApps|Allows applications to be selectable within the dialog|
|---|---|
|kFileOpsOpenApps|Allows the dialog to browse the content of applications|



Note that kFileOpsOpenApps automatically implies kFileOpsSelectApps, although it is valid to specify both flags (kFileOpsSelectApps + kFileOpsOpenApps). 

The name and full path of the folder selected by the user is returned in _cPath_ . Pathnames can be over 255 characters, which was the limit in Studio 8.0.1 or earlier. The function returns true if the user selected a directory and pressed OK. Otherwise, it returns false, meaning that the user pressed Cancel. 

## **Example** 

```
Do FileOps.$changeworkingdir(sys(115)) Returns lError
Do FileOps.$getworkingdir() Returns lWorkDir
```

```
Do FileOps.$selectdirectory(lPath,'Select a folder',lWorkDir) Returns lError
# switches to the 'c:\omnis' folder and prompts the user to select a folder
```

53 



## **FileOps.$setfileinfo()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_FileOps_|NO|All|



## **Syntax** 

**FileOps.$setfileinfo** (cPath,iInformationFlag,vInfoValue,…) 

## **Description** 

Sets file information for the file named _cPath_ . Pathnames can be over 255 characters, which was the limit in Studio 8.0.1 or earlier. 

You can use **$setfileinfo()** to change the read-only and hidden status of a file. You pass the relevant kFileOpsInfo… constant in _iInfoFlag_ , and the new value in _vInfoSetting_ . If desired, you can then pass the other constant and its new value in the next two parameters. The function returns an error code, or zero if successful: see the _FileOps function error codes_ . 

## **Example** 

```
# sets the file 'meths.txt' to be read-only and not hidden
```

## **FileOps.$setunixpermissions()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_FileOps_|NO|Linux, macOS|



## **Syntax** 

FileOps.$setunixpermissions( _cPath,cPermissions_ ) 

## **Description** 

Sets the Unix permissions for the file identified by _cPath._ Pathnames can be over 255 characters, which was the limit in Studio 8.0.1 or earlier. 

The parameter _cPermissions_ has the same syntax as the permissions string returned by _$getunixpermissions()_ . 

## **FileOps.$splitpathname()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_FileOps_|NO|All|



## **Syntax** 

**FileOps.$splitpathname** ( _cPath, &cDriveName,_ [ _&cDirectoryName, &cFileName, &cFileExtension_ ]) 

## **Description** 

Splits the path _cPath_ into _cDriveName_ , _cDirectoryName_ , _cFileName_ , and _cFileExtension_ . Pathnames can be over 255 characters (the limit in Studio 8.0.1 or earlier): the last three parameters are optional (from Studio 10.0.1 onwards). 

The function returns zero if successful, or an error code: see the _FileOps function error codes_ . 

54 



**Example** 

```
Do sys(10) Returns lPath
```

```
# returns the name and path of current library
```

```
Do FileOps.$splitpathname(lPath,lDrive,lDirName,lFilename,lFileExtn) Returns lError
```

```
# under Windows, when lPath = 'C:\OMNIS\EXAMPLES\EXTCOMP.LBS'
```

- `# lDrive returns C:` 

- `# lDirName returns \OMNIS\EXAMPLES\` 

- `# lFileName returns EXTCOMP` 

- `# lFileExtn returns .LBS` 

```
Do FileOps.$splitpathname('c:\omnis',lDrive,lDirName,lFilename,lFileExtn) Returns lError
```

- `# under Windows` 

- `# lDrive returns C:` 

- `# lDirName returns \` 

- `# lFileName returns OMNIS` 

- `# lFileExtn returns (empty)` 

```
Do FileOps.$splitpathname(
```

```
'HD/Omnis/Examples/Extcomp.lbs',lDrive,lDirName,lFilename,lFileExtn) Returns lError
```

```
# under macOS ## note the separator is /, not :
```

- `# lDrive returns HD` 

- `# lDirName returns /Omnis/Examples/` 

- `# lFileName returns Extcomp` 

- `# lFileExtn returns .lbs` 

- `Do FileOps.$splitpathname('/omnis/examples/extcomp.lbs',lDrive,lDirName,lFilename,lFileExtn) Returns lError # under Linux` 

- `# lDrive returns (empty)` 

- `# lDirName returns /omnis/examples` 

- `# lFileName returns extcomp` 

- `# lFileExtn returns .lbs` 

## **FileOps.$writefile()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_FileOps_|NO|All|



## **Syntax** 

**FileOps.$writefile** ( _cFilePath, vVariable_ [, _iEnc_ =kUniTypeUTF8, bBOM=kTrue, bReplace=kTrue]) 

## **Description** 

Writes the file _cFilePath_ with the contents of variable _vVariable_ . Returns an integer error code (zero for success). 

_cFilePath_ (Character 100000000) The pathname of the file. 

_vVariable_ (Variant) The variable into which the file contents will be read. Binary or Character. If it is Character, the file contents are converted to Character using the encoding specified by the iEnc parameter. 

_iEnc_ (Integer 32 bit, default is kUniTypeUTF8) The encoding used to convert the file contents to Character. A kUniType… constant, not kUniTypeBinary or kUniTypeCharacter. Only used when _vVariable_ is a Character variable. 

_bBOM_ (Boolean, default is kTrue) If true, and character data is to be encoded as Unicode, $writefile adds a Unicode Byte Order Marker at the start of the file. 

_bReplace_ (Boolean, default is kTrue) Specifies what occurs if the file already exists before calling FileOps.$writefile(). If bReplace is true FileOps.$writefile() replaces the file; if bReplace if false, FileOps.$writefile() returns an error. 

See FileOps.$readfile(). 

55 



**FileOpsObj.$closefile()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|FileOps|NO|All|



## **Syntax** 

$closefile() 

## **Description** 

Closes the file. 

If you open a file using $openfile(), $openresources(), $create() or $createtmpfile(), then you should close it by calling this function, when you have finished using it. This function does not return a value. 

## **FileOpsObj.$createfile()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|FileOps|NO|All|



## **Syntax** 

$createfile(cFilePath[,cType,cCreator]) 

## **Description** 

Creates and opens an empty file with pathname cFilePath (replaces an existing file with an empty file). For macOS, cType and cCreator are file and creator types for new file. Returns kTrue for success 

If the file already exists, $createfile() replaces it with an empty file. All directories in the pathname specified in the cFilePath parameter must already be present. The optional parameters are only available on macOS. 

## **FileOpsObj.$createtmpfile()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|FileOps|NO|All|



## **Syntax** 

$createtmpfile() 

## **Description** 

Creates and then opens a temporary file, ready for you to write data to it. Returns kTrue for success. 

$createtmpfile() returns a boolean value, which is true if the temporary file was successfully created and then opened. 

After a file has been opened, after using $createtmpfile(), the **$filepath** property of the FileOps object instance will contain the path to the file. This is an alternative or shortcut to returning the file name in the list provided by the $getfileinfo() function. If there is no open file or the file has been closed, $filepath is empty. 

56 



**FileOpsObj.$getfileinfo()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|FileOps|NO|All|



## **Syntax** 

$getfileinfo(iInfoFlags) 

## **Description** 

Returns a list containing file information for the open file associated with the object. iInfoFlags is a combination of kFileOpsInfo… constants; see the FileOps.$getfileinfo static function for a list of kFileOpsInfo constants. If an error occurs, the function returns an empty list. 

After a file has been opened, e.g. after using $createtmpfile(), the **$filepath** property of the FileOps object instance will contain the path to the file. This is an alternative or shortcut to returning the file name in the list provided by the $getfileinfo() function. If there is no open file or the file has been closed, $filepath is empty. 

## **FileOpsObj.$getfilesize()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|FileOps|NO|All|



## **Syntax** 

$getfilesize() 

## **Description** 

Returns the size in bytes of the open file associated with the object. If an error occurs, the function returns -1. 

## **FileOpsObj.$getlasterror()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|FileOps|NO|All|



## **Syntax** 

$getlasterror([&cErrorText]) 

## **Description** 

Returns the error code from the last FileOps object method executed; also optionally populates cErrorText with a description of the error. If no error occurred, returns zero and the error text is empty. 

## **FileOpsObj.$getposition()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|FileOps|NO|All|



57 



**Syntax** 

$getposition() 

## **Description** 

Returns the current position of the open file associated with the object. 

The current position is the byte index to the position in the file where the next function which reads or writes data, will read or write. The first byte in the file has position zero. If an error occurs, the function returns -1. 

## **FileOpsObj.$isopen()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|FileOps|NO|All|



## **Syntax** 

$isopen() 

## **Description** 

Returns true if there is an open file associated with the object, false otherwise. 

## **FileOpsObj.$openfile()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|FileOps|NO|All|



## **Syntax** 

$openfile(cFilePath[,bReadonly=kFalse]) 

## **Description** 

Opens an existing file. cFilePath is the pathname of the file to be opened. Returns kTrue for success. 

The bReadonly parameter is optional. It is a boolean which defaults to false. If you pass true, then $openfile() will open the file in read-only mode. 

$openfile() returns a boolean value, which is true if the file was successfully opened. 

## **FileOpsObj.$openresources()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|FileOps|NO|All|



## **Syntax** 

$openresources(cFilePath[,bReadonly=kFalse]) 

58 



## **Description** 

Opens the resource fork of the specified file. This function applies to macOS only. Returns kTrue for success. 

cFilePath is the pathname of the file for which the resource fork is to be opened. 

The bReadonly parameter is optional. It is a boolean which defaults to false. If you pass true, then $openresources() will open the resource fork in read-only mode. 

$openresources() returns a boolean value, which is true if the resource fork was successfully opened. 

## **FileOpsObj.$readcharacter()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|FileOps|NO|All|



## **Syntax** 

$readcharacter(iEnc,&cData[,&iOff=0,iMax=0,bChkUTF8=kFalse]) 

## **Description** 

Reads characters encoded using iEnc (kUniType… (not Bin/Char)) into cData. Reads entire file, or iMax chars from byte offset iOff and returns next iOff. Returns kTrue for success. 

## **FileOpsObj.$readfile()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|FileOps|NO|All|



## **Syntax** 

$readfile(&xVariable[,iStartPos,iLength]) 

## **Description** 

Reads data from the open file associated with the object. Binary xVariable receives the data read from the file. Returns kTrue for success 

You are recommended to use $readcharacter() to read character data, otherwise you may get unexpected results. 

If you omit iStartPos and iLength, $readfile() reads all the remaining data from the current position to the end of the file; you can set the current position using the function $setposition(). Otherwise, you can specify the position from where the data is to be read, using the iStartPos parameter, and you can specify the number of bytes to read using the iLength parameter. iLength must not exceed the data available from iStartPos to the end of the file. 

$readfile() returns a boolean value, which is true if the data was successfully read. After reading the data, the current position addresses the byte after the last byte read, or end of file, if no further data remains. 

## **FileOpsObj.$selectfilesinsystemviewer()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|FileOps|NO|All|



## **Syntax** 

$selectfilesinsystemviewer(cFileOrFolder[,lFileList]) 

59 



## **Description** 

Opens the system file viewer (Explorer or Finder) and selects the specified file or files. 

cFileOrFolder is either the pathname of a single file to select (when $selectfilesinsystemviewer is called with a single parameter) or the pathname of the folder containing the files to select (when $selectfilesinsystemviewer is called with 2 parameters). 

lFileList is a single column list of file names, specifying the files to be selected in the specified folder. 

The function returns an error code, or zero if successful: See the _FileOps function error codes_ . 

## **FileOpsObj.$setfileinfo()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|FileOps|NO|All|



## **Syntax** 

$setfileinfo(iInfoFlag,vInfoValue,…) 

## **Description** 

Sets a file information item for the open file associated with the object to vInfoValue. iInfoFlag is a kFileOpsInfo… constant. Returns an integer error code, zero for success. 

The function returns an error code, or zero if successful: See the _FileOps function error codes_ . 

## **FileOpsObj.$setfilesize()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|FileOps|NO|All|



## **Syntax** 

$setfilesize(iNewSize) 

## **Description** 

Sets the file size to iNewSize bytes, for the open file associated with the object. Any data after the first iNewSize bytes is lost. Returns kTrue for success. 

$setfilesize() returns a boolean, which is true if the new size was successfully set. 

## **FileOpsObj.$setposition()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|FileOps|NO|All|



## **Syntax** 

$setposition(iNewPos) 

## **Description** 

Sets the current position, for the open file associated with the object. Returns kTrue for success. 

The current position is the byte index to the position in the file where the next function which reads or writes data, will read or write. The first byte in the file has position zero. $setposition() returns a boolean, which is true if the new position was successfully set. 

60 



**FileOpsObj.$writecharacter()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|FileOps|NO|All|



## **Syntax** 

$writecharacter(iEnc,cData[,bAppend=kFalse,bBOM=kTrue]) 

## **Description** 

Writes cData to the file, encoded using the encoding iEnc (kUniType… (not Auto/Bin/Char)). If bAppend is kFalse, the entire file contents are replaced. 

bBOM controls if a BOM is added or not. If true, and the data is to be written at the start of the file, a Unicode Byte Order Marker (BOM) is added at the start of the file. 

Returns kTrue for success. 

## **FileOpsObj.$writefile()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|FileOps|NO|All|



## **Syntax** 

$writefile(xVariable[,iStartPos]) 

## **Description** 

Writes data to the open file associated with the object. Binary xVariable contains the data to write to the file. Returns kTrue for success. 

You are recommended to use $writecharacter() to write character data, otherwise you may get unexpected results. 

By default, $writefile() writes the data starting at the current position. You can specify an alternative position using the iStartPos parameter. 

$writefile() returns a boolean value, which is true if the data was successfully written. After writing the data, the current position addresses the byte after the last byte written, or end of file. 

## **FileOps Function Error Codes** 

The following errors are returned from the FileOps functions. 

|Constant|Code|Description|
|---|---|---|
|kFileOpsNoOperation|999|Operation not supported on this platform|
|kFileOpsUnknownError|998|Unknown error|
|kFileOpsOutOfMemory|12|Out of memory|
|kFileOpsParamError|1|Too few parameters passed|
|kFileOpsOK|0|No Error|
|kFileOpsDirFull|-33|File/Directory full|
|kFileOpsDiskFull|101206|Disk full|
|kFileOpsVolumeNotFound|-35|Specifed volume does not exist|
|kFileOpsDiskIOError|-36|Disk I/O error|
|kFileOpsBadName|-37|Bad fle name or volume name (perhaps zero-length)|
|kFileOpsFileNotOpen|101202|File not open|
|kFileOpsEndOfFile|101207|Logical end-of-fle reached during read operation|



61 



|Constant|Code|Description|
|---|---|---|
|kFileOpsPositionBeforeStart|-40|Attempt to position before the start of the fle|
|kFileOpsTooManyFilesOpen|-42|Too many fles open|
|kFileOpsFileNotFound|101201|File not found|
|kFileOpsHardwareVolumeLock|-44|Volume is locked by a hardware setting|
|kFileOpsFileLocked|101205|File is locked|
|kFileOpsSoftwareVolumeLock|-46|Volume is locked by a software fag|
|kFileOpsMoreFilesOpen|-47|One or more fles are open|
|kFileOpsAlreadyExists|101215|A fle with the specifed name already exists|
|kFileOpsAlreadyWriteOpen|-49|Only one access path to a fle can allow writing|
|kFileOpsNoDefaultVolume|-50|No default volume|
|kFileOpsVolumeNotOnline|-53|Volume not on-line|
|kFileOpsPermissionDenied|101203|Permission denied.|
|kFileOpsReadOnlyFile|-54|Read only fle|
|kFileOpsVolumeAlreadyMounted|-55|Specifed volume is already mounted and on-line|
|kFileOpsBadDrive|-56|No such drive number|
|kFileOpsInvalidFormat|-57|Volume lacks Macintosh-format directory|
|kFileOpsExternalSystemError|-58|External fle system error|
|kFileOpsProblemDuringRename|-59|Problem during rename|
|kFileOpsBadMasterBlock|-60|Master directory block is bad; must re-initialize volume|
|kFileOpsCantOpenLockedFile|-61|Cannot open a locked fle|
|kFileOpsDirectoryNotFound|-120|Directory not found|
|kFileOpsTooManyDirOpen|-121|Too many working directories open|
|kFileOpsCantMoveToOffspring|-122|Attempted to move into offspring|
|kFileOpsNonHFSOperation|-123|Attempt to do HFS operation on a non-HFS volume|
|kFileOpsInternalSystemError|-127|Internal fle system error|



## **flag()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|YES|All|



## **Syntax** 

**flag** () 

## **Description** 

Returns #F. 

## **fld()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Field_|NO|All|



## **Syntax** 

**fld** (string1[,string2],…) 

## **Description** 

Returns the value of the field name given by concatenating or combining one or more _string_ values. 

62 



**Example** 

```
Calculate RATE1 as 10
Calculate RATE2 as 15
```

```
Calculate lFieldValue as fld('RATE','1')
# returns 10
```

```
Calculate lFieldValue as fld('RATE','2')
# returns 15
```

## **fmtdatetime()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Date and Time_|YES|All|



## **Syntax** 

**fmtdatetime** ( _[newformat]_ ) 

## **Description** 

Either sets #FDT to _newformat_ and returns the previous value of #FDT, or if no parameter is supplied returns the current value of #FDT. 

## **fmtdp()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Number_|NO|All|



## **Syntax** 

**fmtdp** ([newdps]) 

## **Description** 

Either sets #FDP to _newdps_ and returns the previous value, or if no parameter is supplied returns the current value of #FDP. 

## **fmtshortdate()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Date and Time_|YES|All|



## **Syntax** 

**fmtshortdate** ( _[newformat]_ ) 

## **Description** 

Either sets #FD to _newformat_ and returns the previous value of #FD, or if no parameter is supplied returns the current value of #FD. 

63 



**fmtshorttime()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Date and Time_|YES|All|



## **Syntax** 

**fmtshorttime** ( _[newformat]_ ) 

## **Description** 

Either sets #FT to _newformat_ and returns the previous value of #FT, or if no parameter is supplied returns the current value of #FT. 

## **fontlist()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Font handling_|NO|Windows, Linux|



## **Syntax** 

**fontlist** ( _listname_ ) 

## **Description** 

Returns a list of fonts currently installed in your system, including the font name and type. 

Note that fontlist() is deprecated. Use _FontOps.$replistfonts_ () or _FontOps.$winlistfonts_ () instead. 

The _listname_ parameter is any list field or variable. A return value of 0 indicates no fonts found or some error, otherwise 1 is returned indicating a list was built. You should define the following columns in your list field or variable. 

|Column 1|Column 2 (Optional)|Column 3 (Optional)|
|---|---|---|
|String variable to hold name of the font|Numeric variable to hold value (0..7) for type of font|String variable to hold a name for the value in column 2. This|
|||will be a combination of “Raster”, “Vector”, “TrueType” together|
|||with “Fixed” or “Proportional”|



## **Example** 

```
Set current list lFontList
Define list {lFontName,lFontType,lFontDesc}
If fontlist(lFontList)<>0
Redraw lists
End If
```

## **FontOps.$replistfonts()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_FontOps_|NO|All|



## **Syntax** 

**FontOps.$replistfonts** ( _list_ ) 

64 



## **Description** 

Populates the specified _list_ with the report fonts installed on your system, and indicates whether or not they are truetype. 

The list must contain two columns, the first character type, the second boolean. The function returns zero for success, less than zero for failure. Having built the list you can search and manipulate the list using the standard list functions and methods. 

## **Example** 

```
Do lFontList.$define(lFont,lTrueType)
Do FontOps.$replistfonts(lFontList)
# returns a list of report fonts
```

```
Do lFontList.$linecount() Returns lNumberOfFonts
# returns the total number of report fonts
```

```
Do tot(lFontList,lTrueType) Returns lNumberOfFonts
```

```
# returns the number of truetype fonts
```

```
Do totc(lFontList,lTrueType=kFalse) Returns lNumberOfFonts
# returns the number of non-truetype fonts
```

## **FontOps.$reptextheight()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_FontOps_|NO|All|



## **Syntax** 

**FontOps.$reptextheight** (font-name|font-table-index,point-size[,font-style,extra-points]) 

## **Description** 

Returns the height in inches/cms (depending on $usecms preferences) of the specified report font. The units of the returned value are determined by $root.$prefs.$usecms. 

## **Example** 

```
Do FontOps.$reptextheight('Times',144) Returns lHeight
# returns 2.24 inches / 5.69 cms
```

```
Do FontOps.$reptextheight('Times',144,,24) Returns lHeight
# returns 2.57 inches / 6.54 cms
```

## **FontOps.$reptextwidth()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_FontOps_|NO|All|



## **Syntax** 

**FontOps.$reptextwidth** (string,font-name|font-table-index,point-size[,font-style]) 

65 



## **Description** 

Returns the width in inches/cms (depending on $usecms preference) required to draw the _string_ using the specified report font. The units of the returned value are determined by $root.$prefs.$usecms. 

## **Example** 

```
Do FontOps.$reptextwidth('Hello WWW','Arial',24) Returns lWidth
# returns 1.83 inches / 4.66 cms
```

```
Do FontOps.$reptextwidth('Hello WWW','Arial',24,kBold+kItalic) Returns lWidth
# returns 1.85 inches / 4.71 cms
```

```
Do FontOps.$reptextwidth('Hello WWW',2,72,kBold+kItalic) Returns lWidth
# returns 5.40 inches / 13.81 cms
```

```
# note that Courier font is at position 2 in #WIRFONTS
```

## **FontOps.$winlistfonts()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_FontOps_|NO|All|



## **Syntax** 

## **FontOps.$winlistfonts** ( _list_ ) 

## **Description** 

Populates the _list_ with the window fonts installed on your system, and indicates whether or not they are truetype. 

The list must contain two columns, the first character type, the second boolean. The function returns zero for success, less than zero for failure. Having built the list you can search and manipulate the list using the standard list functions and methods. 

## **Example** 

```
Do lFontList.$define(lFont,lTrueType)
Do FontOps.$winlistfonts(lFontList)
```

```
# returns a list of windows fonts
```

```
Do lst(lFontList,1,lFont) Returns lFirstFont
```

```
# returns the first font in the list
```

```
Do lst(lFontList,lFontList.$linecount,lFont) Returns lLastFont
# returns the last font in the list
```

## **FontOps.$wintextheight()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_FontOps_|NO|All|



## **Syntax** 

**FontOps.$wintextheight** (font-name|font-table-index,point-size[,font-style,extra-points]) 

66 



## **Description** 

Returns the height in screen units of the specified window font. 

You specify the font using either the _font-name_ or _font-table-index_ . When called with a font table index, **$wintextheight()** uses the window font system table of the current library which can contain up to 15 fonts numbered 1 to 15. You specify the _point-size_ of the font, and you can include a _font-style_ constant and a number of _extra-points_ . 

## **Example** 

```
Do FontOps.$wintextheight('Courier',72) Returns lHeight
```

```
# returns 100 under Windows
```

```
Do FontOps.$wintextheight('Courier',72,,24) Returns lHeight
```

```
# returns 132 under Windows
```

```
Do FontOps.$wintextheight(2,36) Returns lHeight
```

```
# returns 50 under Windows
```

```
# note that Courier font is at position 2 in #WIWFONTS
```

## **FontOps.$wintextwidth()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_FontOps_|NO|All|



## **Syntax** 

**FontOps.$wintextwidth** (string,font-name|font-table-index,point-size[,font-style]) 

## **Description** 

Returns the width in screen units required to display the _string_ using the specified window font. 

You specify the font using either the _font-name_ or _font-table-index_ . When called with a font table index, **$wintextwidth()** uses the window font system table of the current library which can contain up to 15 fonts numbered 1 to 15. You can include a _font-style_ constant, or combination of styles. 

## **Example** 

```
Do FontOps.$wintextwidth('Hello WWW','Courier',36) Returns lWidth
```

```
# returns 243
```

```
Do FontOps.$wintextwidth('Hello WWW','Courier',36,kBold+kItalic) Returns lWidth
# returns 252
```

```
Do FontOps.$wintextwidth('Hello WWW',5,36) Returns lWidth
```

```
# returns 240
```

```
# note that System font is at position 5 in #WIWFONTS
```

## **format()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|NO|All|



67 



**Syntax** 

**format** (format,variable) 

## **Description** 

Applies _format_ to _variable_ and returns the resulting string. _format_ must be a Boolean, date, number or text format: the function expects the type of the _format_ to correspond to the data type of the _variable_ . 

## **formatchunk()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_RESTful_|NO|All|



## **Syntax** 

**formatchunk** ( _data_ ) 

## **Description** 

Formats _data_ and returns a chunk suitable for sending to the client using chunked transfer encoding. _Data_ can be character (which Omnis converts to UTF-8) or binary. 

## **formathttpdate()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_RESTful_|NO|All|



## **Syntax** 

**formathttpdate** ( _omnisdate_ ) 

## **Description** 

Formats the Omnis date-time value _omnisdate_ (assumed to be in UTC) as an HTTP date header value and returns the resulting string. 

## **formatserversentevent()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_RESTful_|NO|All|



## **Syntax** 

**formatserversentevent** (fieldname,fielddata[,fieldname,fielddata]…) 

## **Description** 

Formats data and returns a value suitable for sending as an event in text/event-stream content. Parameters can be character (which Omnis converts to UTF-8) or binary (UTF-8). 

68 



**getdatetime()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Date and Time_|YES|All|



## **Syntax** 

## **getdatetime** () 

## **Description** 

Returns the current system date and time. 

## **getenv()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|NO|All|



## **Syntax** 

**getenv** ( _name_ ) 

## **Description** 

Returns the value of the Omnis process environment variable with the specified _name_ . 

## **Example** 

```
# Get the executable search PATH environment variable
Calculate lVar1 as getenv("PATH")
```

## **getfye()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Date and Time_|NO|All|



## **Syntax** 

**getfye** () 

## **Description** 

Returns the current date of the fiscal year end (note no argument). 

## **Example** 

```
Calculate lDate as setfye('DEC 31')
```

```
# set the fiscal year end to December 31
```

```
Calculate lDate as getfye()
```

```
# returns December 31st set by setfye()
```

69 



**getseed()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Random_|NO|All|



## **Syntax** 

## **getseed** () 

## **Description** 

Returns the current content of the seed as an integer number (note no argument). 

## **Example** 

```
Calculate lResult as getseed()
```

## **getticks()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Date and Time_|YES|All|



## **Syntax** 

**getticks** () 

## **Description** 

Returns the number of ticks elapsed since system boot (for a JavaScript client executed method, since midnight on 1 Nov 2011). A tick is 1/60th of a second. The value can overflow and restart at zero. 

## **getws()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Date and Time_|NO|All|



## **Syntax** 

getws() 

## **Description** 

Returns the day of week which is set as the beginning of the week (note no argument). 

The day of the week is returned as one of the datepart constants: kSunday, kMonday, kTuesday, kWednesday, kThursday, kFriday, kSaturday. 

## **Example** 

```
Calculate lDate as setws(kMonday)
```

```
# set the beginning of the week to Monday
```

```
Calculate lDate as getws()
```

```
# returns 13, the value of the constant kMonday
```

70 



**hexcolor()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|upto 35913_General_|NO|All|
|asof 35914_General_|YES|All|



## **Syntax** 

**hexcolor** ( _string_ ) 

## **Description** 

Returns a color value from the passed hex _string_ . The hex _string_ format is RRGGBB or RRGGBBAA for alpha support. 

## **hsla()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|upto 35913_General_|NO|All|
|asof 35914_General_|YES|All|



## **Syntax** 

**hsla** ( _hue,saturation,light_ [, _alpha_ ]) 

## **Description** 

Returns a color value from the supplied color components: _hue_ range is 0-360; _saturation_ range is 0-100; _light_ range is 0-100; optional _alpha_ range is 0-255. 

## **iconidwithbadge()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|YES|All|



## **Syntax** 

**iconidwithbadge** ( _cIcn,iCnt_ / _cBadgeIcn_ [, _kIconBadge_ …, _iBadgeColor,iBadgeTextColor_ ]) 

## **Description** 

Returns a formatted string for $iconid. _cIcn_ is the main icon (an SVG icon), _iCnt/cBadgeIcn_ control the badge. The _kIconBadge_ … constants control the display of the badge, and _iBadgeColor_ and _iBadgeTextColor_ set the colors of the badge and text. 

When an icon ID uses an SVG icon name, iconidwithbadge() allows you to append additional values to the SVG name to define a badge to be added to the main icon. 

The parameters are: 

|Parameter|Description|
|---|---|
|_cIcn_|the ID of the primary SVG icon for the object / toolbar object|



71 



|Parameter|Description|
|---|---|
|_iCnt_/_cBadgeicn_|the count to be displayed on the badge, or the ID of a smaller secondary icon|
|_kIconBadge_|kIconBadgeAlignTop, kIconBadgeAlignBottom, or the default is the position set by the OS, also kIconBadgeBackgroundHide, see below|
|_ibadgecolor_|the color of the badge, the default is kJSThemeColorSecondary|
|_ibadgetextcolor_|the color of the count, or secondary icon, the default is kJSThemeColorSecondaryText|



The following lines of code set up icon badges for buttons: 

```
Do $cinst.$objs.button.$iconid.$assign(iconidwithbadge( 'tablet_mac', 9 ))
Do $cinst.$objs.button.$iconid.$assign(iconidwithbadge( 'tablet_mac+32x32', 9 ))
Do $cinst.$objs.button.$iconid.$assign(iconidwithbadge( 'tablet_mac', 99, 0, kDarkGreen, kWhite ))
```

Some Omnis objects used fixed icon sizes, such as menu items or tabbar tabs, therefore when applying a badge to these objects you cannot supply an icon size for the primary icon as the size will be fixed by the object, for example: 

```
Do $imenus.NewMenu.$objs.Item.$iconid.$assign(iconidwithbadge( 'tablet_mac', 9 ))
```

When using iconidwithbadge() in a client-executed method, the SVG parameters must be URLs, which can be generated with iconurl() in server-executed code. 

The default icon badge background colour is kJSThemeColorSecondary, while the count or secondary icon is kJSThemeColorSecondaryText (for window class controls the colors are the standard OS colors). 

## **Badge Options** 

The constants **kIconBadgeAlignTop** and **kIconBadgeAlignBottom** can be used in the _kIconBadge_ parameter in iconidwithbadge() to specify the position of the badge. Omitting this or passing 0, Omnis will use the default position for the OS – by default, macOS will draw a badge at the top right of an icon, and Windows at the bottom right. 

The constant **kIconBadgeBackgroundHide** allows you to hide the default colored circle badge when used with a secondary icon. If the badge has a count and not an icon, the badge background is always drawn and this option ignored. For example: 

```
$iconid.$assign(iconidwithbadge( 'tablet_mac', 'star', kBadgeIconHideBackground, kDefault, kRed ))
```

## **iconurl()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|NO|All|



## **Syntax** 

**iconurl** ( _iconid_ ) 

## **Description** 

Returns a URL string from the supplied _iconid_ (integer or string for SVG icons) suitable for use with JavaScript client controls that can display an icon. Note iconurl() must be executed on the server to obtain the correct URL for the icon. 

You can add an icon size constant to the iconid to specify the required size, e.g. ‘car+32x32’, otherwise the icon size is chosen to fill the image area of the control, that is, some controls may restrict the size of icon allowed such as check boxes. 

The server will pick the correct resolution for the icon, if they are available in the icon set (1x or 2x), based on the client resolution. 

**int()** 

72 



|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Number_|YES|All|



## **Syntax** 

**int** (number) 

## **Description** 

Returns the integer part of a _number_ ; it does not round to the nearest integer. 

## **Example** 

```
Calculate lResult as int(23.1056)
# returns 23
```

```
Calculate lResult as int('-2.66')
# returns -2
```

```
Calculate lResult as abs(int(-1.999))
# returns 1
```

## **isclear()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|YES|All|



## **Syntax** 

**isclear** (expression) 

## **Description** 

Returns true if the _expression_ has value NULL, zero (for numeric data types only) or empty. The function returns true for _empty_ and _false_ Boolean values. 

## **isclient()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|YES|All|



## **Syntax** 

**isclient** () no parameters 

## **Description** 

Returns true if the code is currently running in JavaScript client-executed code. 

## **iseven()** 

73 



|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Number_|YES|All|



## **Syntax** 

**iseven** (integer) 

## **Description** 

Returns true if _integer_ is an even number. 

## **isfontinstalled()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Font handling_|NO|Windows, Linux|



## **Syntax** 

**isfontinstalled** ( _fontname_ ) 

## **Description** 

Returns a true or false value indicating whether the named font has been fully installed into your system. 

The _fontname_ argument can be a string literal, character field or variable with a maximum length of 255. 

## **Example** 

## `If not(isfontinstalled('O7Font'))` 

```
OK message {Cannot run library without 'O7Font'}
End If
```

## **isheadless()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|NO|All|



## **Syntax** 

**isheadless** () 

## **Description** 

Returns true if Omnis is currently running as a headless server with no GUI. 

## **isleopard()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|NO|All|



74 



**Syntax** 

**isleopard** () 

## **Description** 

**Deprecated.** Please note that as of Studio 10.1 revision 23638, individual _is…()_ functions are deprecated in favour of the _systemversion()_ function- which supports all recent operating system versions. 

Returns true if the current operating system is Mac OS X Leopard (10.5) or later. 

## **islion()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|NO|All|



**Syntax islion** () 

## **Description** 

**Deprecated.** Please note that as of Studio 10.1 revision 23638, individual _is…()_ functions are deprecated in favour of the _systemversion()_ function- which supports all recent operating system versions. 

Returns true if the current operating system is Mac OS X Lion (10.7) or later. 

## **ismountainlion()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|NO|All|



## **Syntax** 

**ismountainlion** () 

## **Description** 

**Deprecated.** Please note that as of Studio 10.1 revision 23638, individual _is…()_ functions are deprecated in favour of the _systemversion()_ function- which supports all recent operating system versions. 

Returns true if the current operating system is Mac OS X Mountain Lion (10.8) or later. 

## **isnull()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|YES|All|



## **Syntax** 

**isnull** (expression) 

75 



## **Description** 

Returns true if the _expression_ has value NULL. 

Also returns true if _fieldname_ , a field in the current record, is null. A null value is one where no value has been entered and the field definition is **Can be null** without **Insert as Empty.** 

## **Example** 

```
Calculate lVar1 as #NULL
```

```
Calculate lBoolean as isnull(lVar1)
# returns true because lVar1 is null
```

## **isnumber()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_String_|NO|All|



## **Syntax** 

**isnumber** (string[,decimal-char][,thousands-char]) 

## **Description** 

Returns kTrue if the specified _string_ can be evaluated as a number; kFalse otherwise. 

The optional parameters can be used to define the decimal and thousand separator. If the optional parameters are not specified the default separators are used, a ‘.’ for the decimal and a ‘,’ for the thousand. 

## **Example** 

```
Calculate lStatus as isnumber(lString)
```

```
# lStatus is kTrue if lString can be evaluated as a number
```

## **iso8601toomnis()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|upto 35924 Date and Time|NO|All|
|asof 35925 Date and Time|YES|All|



## **Syntax** 

**iso8601toomnis** ( _ciso8601,bneedtime,bHasTimeZone[,cerrtext]_ ) 

## **Description** 

Converts an ISO8601 date/date-time string to Omnis date-time and returns result (in UTC if cISO8601 contains time zone). Returns NULL and cErrText if an error occurs. 

The date string is in the form: YYYY-MM-DDTHH:MM:SS.FFFZ rounding FFF into the hundredths field appropriately. The representations in the date string are: 

YYYY-MM-DD Date: Year, month, day T Date time delimeter HH:MM:SS.FFF Time: Hours, minutes, seconds, fractions of a second 

76 



UTC offset: Z means zero UTC offset, or add +/- offset 

Z 

For more information about ISO8601 look up: https://en.wikipedia.org/wiki/ISO_8601 

Note that for a RESTful service, you should always use time zones for input date time values, so you would always pass bHasTimeZone as kTrue to iso8601toomnis() if you are passing bNeedTime as kTrue. 

## **isodd()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Number_|YES|All|
|**Syntax**|||
|**isodd**(integer)|||
|**Description**|||
|Returns true if_integer_is an odd number.|||



## **isoweek()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Date and Time_|NO|All|
|**Syntax**|||
|**isoweek**(_date_)|||
|**Description**|||
|Returns the ISO 8601 standard week number for the week containing the specifed_date_.|||



## **Example** 

`Calculate lDate as isoweek(#D) # returns the current ISO week number` **isoweekstart()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Date and Time_|NO|All|
|**Syntax**|||
|**isoweekstart**(_year,week_)|||



## **Description** 

Returns the date of day 1 of the specified ISO _week_ number (1-53) of the specified _year_ . 

77 



**issnowleopard()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|NO|All|



## **Syntax** 

**issnowleopard** () 

## **Description** 

**Deprecated.** Please note that as of Studio 10.1 revision 23638, individual _is…()_ functions are deprecated in favour of the _systemversion()_ function- which supports all recent operating system versions. 

Returns true if the current operating system is Mac OS X Snow Leopard (10.6) or later. 

## **isunicode()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Unicode_|YES|All|



## **Syntax** 

**isunicode** () 

## **Description** 

Always returns true because Omnis Studio 5.0 and later always supports Unicode. 

## **isvista()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|NO|All|



## **Syntax** 

**isvista** ([themed=kfalse]) 

## **Description** 

**Deprecated.** Please note that as of Studio 10.1 revision 23638, individual _is…()_ functions are deprecated in favour of the _systemversion()_ function- which supports all recent operating system versions. 

For themed = kFalse, returns true if the current operating system is Windows Vista or later; for themed = kTrue, returns true if the current operating system is Windows Vista or later with a themed appearance. 

## **iswindows10()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|NO|All|



78 



## **Syntax** 

**iswindows10** ([themed=kfalse]) 

## **Description** 

**Deprecated.** Please note that as of Studio 10.1 revision 23638, individual _is…()_ functions are deprecated in favour of the _systemversion()_ function- which supports all recent operating system versions. 

For themed = kFalse, returns true if the current operating system is Windows 10 or later; for themed = kTrue, returns true if the current operating system is Windows 10 or later with a themed appearance. 

## **iswindows11()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|NO|All|



## **Syntax** 

**iswindows11** ([themed=kfalse]) 

## **Description** 

**Deprecated.** Please note that as of Studio 10.1 revision 23638, individual _is…()_ functions are deprecated in favour of the _systemversion()_ function- which supports all recent operating system versions. 

For themed = kFalse, returns true if the current operating system is Windows 11 or later; for themed = kTrue, returns true if the current operating system is Windows 11 or later with a themed appearance. 

## **iswindows7()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|NO|All|



## **Syntax** 

**iswindows7** ([themed=kfalse]) 

## **Description** 

**Deprecated.** Please note that as of Studio 10.1 revision 23638, individual _is…()_ functions are deprecated in favour of the _systemversion()_ function- which supports all recent operating system versions. 

For themed = kFalse, returns true if the current operating system is Windows 7 or later; for themed = kTrue, returns true if the current operating system is Windows 7 or later with a themed appearance. 

## **iswindows8()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|NO|All|



## **Syntax** 

**iswindows8** ([themed=kfalse]) 

79 



## **Description** 

**Deprecated.** Please note that as of Studio 10.1 revision 23638, individual _is…()_ functions are deprecated in favour of the _systemversion()_ function- which supports all recent operating system versions. 

For themed = kFalse, returns true if the current operating system is Windows 8 or later; for themed = kTrue, returns true if the current operating system is Windows 8 or later with a themed appearance. 

## **iswindows81()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|NO|All|



## **Syntax** 

**iswindows81** ([themed=kfalse]) 

## **Description** 

**Deprecated.** Please note that as of Studio 10.1 revision 23638, individual _is…()_ functions are deprecated in favour of the _systemversion()_ function- which supports all recent operating system versions. 

For themed = kFalse, returns true if the current operating system is Windows 8.1 or later; for themed = kTrue, returns true if the current operating system is Windows 8.1 or later with a themed appearance. 

## **iswindowsserver()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|NO|All|



## **Syntax** 

## **iswindowsserver** () 

## **Description** 

Returns true if the current operating system is a Windows Server operating system. 

## **JavaObjs Library.$addclass()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_JavaObjs Library_|NO|All|



## **Syntax** 

**JavaObjs Library.$addclass** (group,classfilename,[classpath]) 

## **Description** 

Adds a class to the specified group constant. 

80 



**JavaObjs Library.$resetclasscache()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_JavaObjs Library_|NO|All|



## **Syntax** 

## **JavaObjs Library.$resetclasscache** () 

## **Description** 

Deletes the Java objects class cache file, allowing the Java objects library to rebuild it the next time Omnis starts up; any classes added with $addclass will be lost from the cache. 

## **join()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_String_|YES|All|



## **Syntax** 

**join** ( _list_ [, _delimiter_ =ktab, _column_ =1, _stripwhite_ =kfalse, _quotechar_ =”]) 

## **Description** 

Returns a string of all _column_ values in _list_ , delimited by _delimiter_ . Options _stripwhite_ to strip leading and trailing whitespace, and/or _quotechar_ to quote column values (escaping quotes as 2 quotes). 

## **jst()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_String_|YES|All|



## **Syntax** 

**jst** (string1,number1[,string2,number2]…) 

## **Description** 

Returns a string containing the specified _string_ left or right justified with sufficient spaces added to make a total length specified by _number_ . 

The **jst()** function also includes concatenation. If _number_ is negative the resulting _string_ is right justified, if the _number_ is positive the _string_ is left justified; _number_ must be in the range 1 to 999. 

```
jst('This is left justified',30)
# gives
|This is left justified |
```

```
jst('This is right justified',-30)
# gives
| This is right justified|
```

81 



When you define the columns for a list, **jst()** lets you fix the column width and using a non-proportional font the list columns will line up properly. For example, the calculation for a list containing the fields CODE and COMPANY could be 

## `jst(CODE,7,COMPANY,25)` 

The **jst()** function also includes concatenation, for example: 

```
jst(p1,p2,p3,p4,p5,p6,...)
# is the same as
con(jst(p1,p2),jst(p3,p4),jst(p5,p6),...)
```

However it has a limit of 100 parameters, but you can exceed this limit by using _Calculate CVAR1 as_ jst _(CVAR2,CVAR3)_ where CVAR2 has 99 items and CVAR3 has 99 items, and so on. 

## **Formatting Strings Using jst()** 

The **jst()** function can take a string for the second argument instead of a number, that is 

## **jst** ( _string1_ , _string1_ [, _string2_ , _string2_ ]…) 

This form of **jst()** formats the first _string1_ argument in a way controlled by the second _string2_ argument. The second argument consists of a series of formatting options which you can use separately or together. Each option is represented by one or more characters. The order of the various formatting options is not important but the case is. 

|^n|(caret) causes the data to be centered in the feld n characters wide.jst(‘abc’,‘^5’) ## returns ‘abc’jst(FIELD,‘^25’) ## as a list|
|---|---|
||calculation will center the FIELD values in a column 25 characters wide|
|£|places a £ sign in front of the data. The data must be a number or an integer.jst(TOTAL,‘£’) ## returns ‘£12.12’ if TOTAL = 12.12|
|$|places a $ sign in front of the data. The data must be a number or an integer.jst(TOTAL,‘$’) ## returns ‘$12.12’ if TOTAL = 12.12|
|<|left justifcation, overriding the default set up in a report class. This is used by the Ad hoc report generator to control the|
||justifcation of felds.|
|Pc|causes the part of the feld not flled by the data to be flled by character c.jst(‘abc’,‘-5P*’) ## returns ‘**abc’|
|X|causes the data to be truncated if its length exceeds the feld length. The default is not to truncate.jst(‘abcdef’,‘4’) ##|
||returns ‘abcdefjst(’abcdef’,‘4X’) ## returns ‘abcd’|
|U|causes the data to be converted to upper case.jst(‘this IS it’,‘U’) ## returns ‘THIS IS IT’|
|L|causes the data to be converted to lower case. jst(‘THIS is IT’,‘L’) ## returns ‘this is it’|
|C|causes the data to be capitalized.jst(‘this is it’,‘C’) ## returns ‘This Is It’jst(‘THIS IS IT’,‘C’) ## returns ‘This Is It’jst(‘this IS IT’,‘C’)|
||## returns ‘This Is It’|
|Nnn|causes the data to be treated as a fxed decimal number with nn decimal places. If nn is not specifed, a suitable number of|
||decimal places is used.jst(0.235,‘N’) ## returns ‘0.235’jst(0.235,‘N2’) ## returns ‘0.24’|
|Fnn|causes the data to be treated as a foating decimal number with format specifed by nn. The nn argument can be a positive|
||or negative number and has the same meaning as described for the #FDP variable. If nn is not specifed, it defaults to the|
||current value of #FDP. jst(12.35,‘-10F9’) ## returns ‘12.35’jst(12.35,‘-10F-9’) ## returns ‘1.23500000e+001’jst(12.35,‘-10F-3U’) ##|
||returns ‘1.24E+001’|
|D|causes the data to be treated as a date. The default formatting string is #FD, but you can specify a formatting string as|
||described later. Note - JavaScript client-executed methods do not support the D option.jst(‘26/11/97’,‘DC’) ## returns ‘26 Nov|
||97’ if #FD = ‘D m Y’|
|DT|causes the data to be treated as a long date and time. The default formatting string is #FDT but you can specify a|
||formatting string using the : (colon) argument as described below. Note - JavaScript client-executed methods do not|
||support the DT option. jst(#D,‘DT’) ## returns ‘26 Nov 97 15:30’ if #FDT is ‘D m Y H:N’|
|T|causes the data to be treated as a time using the formatting string_#FT_. You can include a format string using the : (colon)|
||argument as described below. Note - JavaScript client-executed methods do not support the T option.jst(‘0620’,‘T’) ##|
||returns ‘06:20’ if #FT = ‘H:N’|
|A|displays a null value as ‘NULL’.jst(Field1,‘A’) ## returns ‘NULL’ when Field1 is null|
|B|causes the data to be treated as Boolean.jst(1,‘LB’) ## returns ‘yes’|
|E|applies to numbers only and turns on the ‘Zero shown empty’ attribute.jst(0,‘N2’) ## returns ‘0.00’jst(0,‘N2E’) ## returns ‘’ | | ,|
||| (comma) applies to numbers only and turns on the ’Shown like 1,234’ attribute.jst(1234,‘N2’) ## returns|
||‘1234.00’jst(1234,‘N2,’) ## returns ‘1,234.00’|
|(|(open bracket) applies to numbers only and turns on the ‘Shown like (1234)’ attribute.jst(-1234,‘N2’) ## returns|
||‘-1234.00’jst(-1234,‘N2(’) ## returns ‘(1234.00)’jst(1234,‘N2(’) ## returns ‘1234.00’|



82 



) 

(close bracket) applies to numbers only and turns on the ‘Shown like 1234-’ attribute.jst(-1234,‘N2)’) ## returns ‘1234.00-’jst(1234,‘N2)’) ## returns ‘1234.00’ 

+ (plus sign) applies to numbers only and causes positive numbers to be shown with a “+” sign.jst(1234,‘N2+’) ## returns ‘+1234.00’jst(1234,‘N2)+’) ## returns ‘1234.00+’ 

: (colon) characters following a colon are interpreted as a formatting string. This must be the last option since all characters following it become part of the formatting string. The meaning of the formatting string depends on the type of the data. 

The formatting string has a similar format to #FDT if the data is a date/time value, using the following characters: 

|Y|Year (99)|H|Hour (0..23)|
|---|---|---|---|
|y|Year (1999)|h|Hour (1..12)|
|C|Century (19)|N|Minutes|
|M|Month (06)|S|Seconds|
|m|Month (JUN)|s|Hundredths|
|n|Month (June)|A|AM/PM|
|D|Day (12)|V|Short day of week (Fri)|
|d|Day (12th)|E|Day of year (1–366)|
|W|Day of week (5)|G|Week of year (1–52)|
|w|Day of week (Friday)|F|Week of month (1–6)|



For example: 

```
jst(#D,'D:w, d n CY')
# returns 'Saturday, 29th November 1997'
cap(jst(#D,'D:V d n Y'))
# returns 'Sat 29th Nov 97'
```

The formatting string has a similar format to #FT if the data is a time value. #FT is used as the formatting string if a formatting string is not specified for a time. 

```
jst(#T,'T:H-N') ## returns '14-07'
```

If the data is neither a date nor a time value, and if the formatting string contains an X, the data value is inserted at the position of the X to produce the data value. 

```
jst(0,'BC:The answer is X!')
```

```
# returns 'The answer is No!'
```

The formatting string is concatenated to the left of the data value if the formatting string does _not_ contain an X. The data value is left unchanged if a formatting string is not specified. 

```
jst(12,'-7N2:$') ## returns ' $12.00'
jst(12,'-7N2:£') ## returns ' £12.00'
jst(12,'-8N2:DM') ## returns ' DM12.00'
```

## **lday()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Date and Time_|NO|All|



**Syntax** 

**lday** (datepart,date) 

83 



## **Description** 

Returns the date of the last day of the year, month, week or quarter in which the specified date falls. datepart can be kYear, kQuarter, kMonth, or kWeek. 

The period is specified using one of the following datepart constants: kYear, kQuarter, kMonth, kWeek. 

## **Example** 

```
Calculate lDate as lday(kWeek,#D)
```

```
# returns May 11 2003, assume #D is May 8, 2003
```

```
Calculate lDate as lday(kMonth,#D)
```

```
# returns May 31 2003, assume #D is May 8, 2003
```

## **left()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_String_|YES|All|
|**Syntax**|||
|**left**(string,n)|||
|**Description**|||
|Returns the substring comprising the frst_n_characters|of the_string_.||
|**Example**|||
|`Calculate lResult as left('Raining',4)`|||
|`# returns 'Rain'`|||
|**len()**|||



|Function group|Execute on client|Platform(s)|
|---|---|---|
|_String_|YES|All|
|**Syntax**|||
|**len**(string)|||
|**Description**|||
|Returns the length of a_string_(number of characters).|||



## **Example** 

```
Calculate lResult as len('Hello there!')
# returns 12
```

```
Calculate lResult as len(abs(-10.25))
# returns 5 as it is the same as len(10.25)
```

```
Calculate lResult as len('Omnis')+20
# returns 25
```

84 



## **list()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_List_|YES|All|



## **Syntax** 

**list** (row1[,row2]…) 

## **Description** 

Returns a list from a number of _row_ variables of identical structure, that is, the data type of each column in each row variable should match. 

In the following example, one row in the list is created for each row variable passed. If the type of a particular column in the list does not match the type of a row variable column, **list()** tries to convert the row variable column to that of the list column, from number to string. If the column type cannot be converted the column is left blank. 

## **Example** 

```
Set current list lList
Define list {lCol1,lCol2,lCol3}
Calculate lList as list(lRow1,lRow2,lRow3)
```

```
# returns a list from row variables, lRow1, lRow2 and lRow3
```

## **listenv()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|NO|All|



## **Syntax** 

**listenv** () 

## **Description** 

Returns a 2 column list of the Omnis process environment variables. Column 1 contains the variable name, and column 2 the variable value. The list is sorted by the variable name column (case insensitive). 

## **Example** 

```
# Get the list of environment variables
```

```
# There is no need to define the list first; the returned list has 2 character columns, name and value
Calculate lList as listenv()
```

## **ln()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Logarithmic_|YES|All|



## **Syntax** 

**ln** (number) 

85 



## **Description** 

Returns the log to base e (the natural logarithm) of a _number_ ; or -1e100 if _number_ <= 0. 

## **Example** 

```
Calculate lResult as ln(exp(0.5))
# returns 0.5
```

## **locale()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Unicode_|YES|All|



## **Syntax** 

**locale** ([locfile=kfalse]) 

## **Description** 

Returns either the locale string for the user locale in which the program is running, or in the fat client if _locfile_ is kTrue, the current localisation data file locale. 

## **loctoutc()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Date and Time_|NO|All|



## **Syntax** 

**loctoutc** ( _datetime_ ) 

## **Description** 

Converts the _datetime_ (or time) from the local timezone to UTC (Coordinated Universal Time), and returns the result. 

## **log()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Logarithmic_|YES|All|



## **Syntax** 

**log** (number) 

## **Description** 

Returns the log to base 10 of a _number_ ; or -1e100 if _number_ <= 0. 

86 



## **Example** 

```
Calculate lResult as log(100)
# returns 2
```

```
Calculate lResult as log(0.001)
# returns -3
```

## **lookup()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Lookup_|NO|All|



## **Syntax** 

**lookup** ([refname,]searchvalue[,fieldnumber]) 

## **Description** 

Returns a field value from another data file _refname_ (opened as a lookup file) using a _searchvalue_ . 

The _fieldnumber_ argument specifies the particular field in the lookup file to be returned by the function. Each lookup file is opened using the _Open lookup file_ command at which time a reference label is assigned to that lookup. 

If you omit the third argument, the value of the second field is returned by default. If one argument is given, the default lookup file is used, that is, the lookup file which was opened without a reference label, or the first lookup file opened if all have labels. 

If no exact match is found, an empty value is returned. All field types are returned, including pictures and long text. 

## **Example** 

```
Open lookup file {City/Cities.df1/FCITY/1}
```

```
# Reference name is City, file class FCITY
```

```
OK message {CNAME is [lookup('City','FOS',2)]}
# Uses first field in FCITY as the index
```

## **low()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_String_|YES|All|



## **Syntax** 

**low** (string) 

## **Description** 

Returns the lower case representation of a _string_ . Any non-alphabetic characters in the strings are unaffected by low(). 

87 



## **Example** 

```
Calculate lString as low('DAVID')
# returns 'david'
```

```
Calculate lString as low('OrAcLe8')
# returns 'oracle8'
```

```
Calculate lString as low('1017')
# returns '1017’
```

```
Calculate lString as mid(low('PERIPHERAL'),3,3)
# returns 'rip'
```

## **lst()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_List_|NO|All|



## **Syntax** 

**lst** ([[listname,]linenumber,]fieldname) 

## **Description** 

Returns the value of _fieldname_ from a line specified by _linenumber_ in a list specified by _listname_ . For client-executed methods _listname_ must be specified. 

The _fieldname_ argument must be a field stored in the list, not a constant or expression. If _listname_ is not specified the current list is used. If only the _fieldname_ argument is specified the current line of the current list is used. 

## **Example** 

```
Calculate lResult as lst(lList,23,lCol1)
```

```
# returns lCol1 field value stored at line 23 of list lList
```

```
Calculate lResult as lst(23,lCol1)
```

```
# returns lCol1 field value stored in line 23 of the current list
```

```
Calculate lResult as lst(lCol1)
```

```
# returns lCol1 field value stored at current line of current list
```

```
Calculate lResult as lst(lList,0,#LM)
```

```
# returns the maximum number of lines in list lMyList
```

## **max()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Lookup_|YES|All|



## **Syntax** 

**max** (value1[,value2]…) 

88 



## **Description** 

Returns the maximum value from a list of values. The values should all be numbers when numeric comparison is used or all strings when string comparison is used. 

## **Example** 

```
Calculate lResult as max(3,6,2,7)
# returns 7
```

```
Calculate lResult as max('dagger','dog','dig')
```

```
# returns 'dog'
```

## **maxc()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_List_|NO|All|



## **Syntax** 

**maxc** (listname,column[,ignore-nulls]) 

## **Description** 

Returns the maximum value for a list column specified by _listname_ and _column_ . maxc() can only be used with columns defined using variables so it cannot be used with lists defined from a SQL class. 

If you set _ignore_nulls_ to 1, null values are ignored and not counted. If you omit this parameter or it evaluates to zero, nulls are treated as zero values and are counted. 

## **Example** 

```
Calculate lMax as maxc(lInventory,lQuantity)
```

```
# returns the maximum value in the lQuantity column of lInventory
```

## **mid()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_String_|YES|All|



## **Syntax** 

**mid** (string,position,length) 

## **Description** 

Returns a substring of a specified _length_ , starting at a specified _position_ , from a larger _string_ . 

If _position_ is less than 1, or greater than the length of the _string_ , the result is an empty string. If _length_ is greater than the maximum length of any substring of _string_ starting at _position_ , the returned substring will be the remainder of _string_ starting at position. If you omit _length_ , the remainder of the _string_ from _position_ is returned. 

89 



## **Example** 

```
Calculate lString as mid('Information',6,3)
# returns 'mat'
```

```
Calculate lString as int(mid(12.45,2,3))
# returns 2 as it is the same as int('2.4')
```

```
Calculate lString as mid('interaction',6,24)
```

```
# returns 'action'
```

## **min()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Lookup_|YES|All|



## **Syntax** 

**min** (value1[,value2]…) 

## **Description** 

Returns the minimum value from a list of values. The values should all be numbers when numeric comparison is used or all strings when string comparison is used. 

## **Example** 

```
Calculate lResult as min(3,6,2,7)
```

```
# returns 2
```

```
Calculate lResult as min('cat','dog','apple')
```

```
# returns 'apple'
```

## **minc()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_List_|NO|All|



## **Syntax** 

**minc** (listname,column[,ignore-nulls]) 

## **Description** 

Returns the minimum value for a list column specified by _listname_ and _column_ . minc() can only be used with columns defined using variables so it cannot be used with lists defined from a SQL class. 

If you set _ignore_nulls_ to 1, null values are ignored and not counted. If you omit this parameter or it evaluates to zero, nulls are treated as zero values and are counted. 

## **Example** 

```
Calculate lMin as minc(lInventory,lQuantity)
```

```
# returns the minimum value in the lQuantity column of lInventory
```

90 



## **mod()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Number_|YES|All|



## **Syntax** 

**mod** (number1,number2) 

## **Description** 

Returns the remainder of a number division, that is, when _number1_ is divided by _number2_ to produce a remainder; it is a true modulus function. 

mod() checks for integer arguments, and if so uses integer rather than floating point operations to determine its result. The result is still returned as a number rather than an integer. 

## **Example** 

```
Calculate lResult as mod(6,4)
# returns 2
```

```
Calculate lResult as mod(4,6)
# returns 4
```

```
Calculate lResult as mod(-5,-2)
# returns -1
```

## **mousedn()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Mouse_|NO|All|



## **Syntax** 

**mousedn** () 

## **Description** 

Returns true if the mouse button is held down, otherwise returns false (note no argument). This function returns a Boolean value describing the state of mouse button (the left-hand mouse button under Windows). 

_Note: This function is for desktop apps using Window classes only, not web or mobile apps._ 

## **mouseover()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Mouse_|NO|All|



## **Syntax** 

**mouseover** ( _constant_ ) 

**mouseover** (constant[, _tablefield_ ]) 

91 



## **Description** 

_Note: This function is for desktop apps using Window classes only, not web or mobile apps._ 

Returns information about the mouse position defined by a predefined _constant_ at the instant the function is evaluated. 

Returns information about the mouse position defined by a mouseover _constant_ (e.g. kMLine) when mouseover is called. If using kMItemref and _tablefield_ is kTrue, enterable grid row fields are checked; in this case, the function will return a reference to the field under the mouse in a complex grid. 

The function only works in an “open” user-defined window (not reports or searches). Moreover, it returns references only for fields and not background objects (text and graphic objects). 

The mouse position is returned in a variety of ways depending on the constant you use. You can use the following constants: 

|Constant|Description|
|---|---|
|kMCharpos|returns the nth character in an edit feld.|
|kMComplexGridRow|returns the row of a Complex grid the pointer is over|
|kMHorz|returns the horizontal position of the mouse relative to the topmost open user-defned window;|
||if no user-defned window is open, returns the horizontal position of the mouse relative to the|
||Omnis application window|
|kMItemref|returns a reference to the object under the mouse. The window instance itself can be returned|
||as item 0 of the window.|
|kMLine|returns the line number for a list.|
|kMPLine|returns the line of the parent list the mouse is over.|
|kMScreenPos|returns a row with 2 columns, h and v, which are the horizontal and vertical position of the|
||pointer (mouse) in screen coordinates, respectively|
|kMVert|returns the vertical position of the mouse relative to the topmost open user-defned window; if|
||no user-defned window is open, returns the relative position to the Omnis application window|



## **mouseup()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Mouse_|NO|All|



## **Syntax** 

## **mouseup** () 

## **Description** 

Returns true if the mouse button is released after having been pressed, otherwise returns false (note no argument). 

_Note: This function is for desktop apps using Window classes only, not web or mobile apps._ 

## **msgcancelled()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|YES|All|



## **Syntax** 

## **msgcancelled** () 

## **Description** 

Returns true if the user Cancel button is pressed on a message box. 

For example, you can use this to distinguish between No and Cancel on a Yes/No message which both clear the flag. 

92 



## **Example** 

```
Yes/No message (Cancel button) {Do you want to proceed?}
If flag false
```

```
If not(msgcancelled())
```

```
# user chose No
End If
```

```
Else
# user chose Yes
End If
```

## **nam()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Field_|NO|All|



## **Syntax** 

**nam** (fieldname[,doitems=ktrue]) 

## **Description** 

Returns the name of a field as a string; _fieldname_ must be a field name or variable, not a constant or expression. If _doitems_ is true, nam() follows item references. 

## **Example** 

```
Calculate lFieldName as nam(CCODE)
```

```
# returns the string 'CCODE'
```

```
Calculate lFieldName as nam(#SUBFLD)
```

```
# returns the name of the subtotal field
```

## **natcmp()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_String_|NO|All|



## **Syntax** 

**natcmp** (value1,value2) 

## **Description** 

Returns the result of comparing two values using the national sort ordering. Returns 0 if the strings are equal, 1 if _value1_ > _value2_ , and -1 if _value1_ < _value2_ . 

Both values are converted to strings before the comparison is made. **natcmp()** uses the same rules for comparing the strings as it does for normal strings, except that it uses the national sort ordering. 

## **Example** 

```
Calculate lResult as natcmp(lValue1,lValue2)
# returns 0 if values are equal
```

93 



## **nday()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Date and Time_|NO|All|



## **Syntax** 

**nday** (datepart,date) 

## **Description** 

Returns the date of the day after the specified _date_ when the _datepart_ constant is set to kDay. 

However, if one of the day of the week constants is used, this function returns the date of that day of the week following the specified _date_ . 

The datepart constants that you can use are: kDay, kSunday, kMonday, kTuesday, kWednesday, kThursday, kFriday, kSaturday. 

## **Example** 

```
Calculate lDate as nday(kDay,#D)
```

```
# returns May 9 2003, assume #D is May 8, 2003
```

```
Calculate lDate as nday(kMonday,#D)
```

```
# returns May 12 2003, which is the next Monday after #D, assume #D is May 8, 2003
```

## **nfc()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Unicode_|NO|All|



## **Syntax** 

**nfc** (string) 

## **Description** 

Carries out canonical decomposition followed by canonical composition on the _string_ and returns the normalized string. 

## **nfd()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Unicode_|NO|All|



## **Syntax** 

**nfd** (string) 

## **Description** 

Carries out canonical decomposition on the _string_ and returns the normalized string. 

94 



**not()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|YES|All|



## **Syntax** 

**not** (expression) 

## **Description** 

Returns the logical Not of an _expression_ . 

All expressions in Omnis have a Boolean (truth) value. Firstly, non-zero numeric values (including negative values) are TRUE, zero values are FALSE. Secondly, string values are TRUE or FALSE depending on their numeric equivalent. String ‘1’ has boolean value 1, therefore _not(‘1’)_ is 0. ‘Bill’ has boolean value 0, ‘YES’ has numeric value 0. 

The numeric value of an expression that evaluates to true is 1, therefore _not(true)_ is 0. Similarly, _not(false)_ is 1. 

You can also use **not()** to make method code more readable. 

## **Example** 

```
Calculate lVar1 as not(2501)
# returns 0
```

```
Calculate lVar1 as not('Hello there!')
```

```
# is the same as not(0) which returns 1
```

```
Calculate lVar1 as not(31<45)
```

```
# is the same as not(true) which returns false
```

```
Do method ProcessList Returns Done
```

```
If not(Done)
# do something
End If
```

```
# can be used to make code more readable
```

## **OIMAGE.$getdimensions()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_OIMAGE_|NO|All|



## **Syntax** 

**OIMAGE.$getdimensions** ( _xImage, &iWidth, &iHeight_ [,& _cErrorText_ ]) 

## **Description** 

Returns the dimensions in _iWidth_ and _iHeight_ of the image _xImage_ . Returns Boolean true for success, or false and _cErrorText_ if an error occurs. 

_xImage_ A binary variable containing the image. 

_iWidth_ and _iHeight_ are 32 bit integer variables that receive the pixel Width and Height of the image. 

_cErrorText_ The error text returned from the function. 

95 



**OIMAGE.$makeqrcode()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_OIMAGE_|NO|All|



## **Syntax** 

**OIMAGE.$makeqrcode** ( _vData, &xQrCode_ [, _iFmt_ =kOIMAGEfmtPNG, _iSizePNG_ =256, _iECL_ =kOIMAGEerrHigh, _iBorder_ =4, _&cErrorText_ ]) 

**OIMAGE.$makeqrcode** ( _vData, &xQrCode_ [, _iFmt_ =kOIMAGEfmtPNG, _iSizePNG_ =256, _iECL_ =kOIMAGEerrHigh, _iBorder_ =4, _&cErrorText_ , _&wCenterImg_ ]) 

## **Description** 

Makes a QR Code for the specified binary or character vData. Returns Boolean true and xImage for success, or false and cErrorText if an error occurs. 

**vData:** Binary or character data to be represented by the QR Code.The method converts character data to UTF-8 before encoding it. The amount of data that can be encoded is limited, and varies according to iECL. See the QR Code standard. 

**xQrCode:** Binary variable that receives the generated QR Code 

**iFmt:** A kOIMAGEfmt… constant that specifies the format of the generated QR Code. kOIMAGEfmtPNG or kOIMAGEfmtSVG 

**iSizePNG:** The width and height in pixels of the QR Code, when generating kOIMAGEfmtPNG. Must be between 32 and 262144 inclusive 

**iECL:** A kOIMAGEerr… constant that specifies the error correction level supported by the generated QR Code: 

## 1. **kOIMAGEerrLow** 

The QR Code can tolerate about 7% erroneous codewords 

2. **kOIMAGEerrMedium** 

The QR Code can tolerate about 15% erroneous codewords 

## 3. **kOIMAGEerrQuartile** 

The QR Code can tolerate about 25% erroneous codewords 

## 4. **kOIMAGEHigh** 

The QR Code can tolerate about 30% erroneous codewords 

**iBorder:** The number of border modules to surround the QR Code. 

**cErrorText:** Receives the error text if an error occurs. 

**wCenterImg:** Adds an icon image to the center of the generated QR code: see below. 

## **Adding an image** 

The **wCenterImg** parameter controls how an icon can be overlaid after a QR code has been created; this only works for kOIMAGEfmtPNG output QR images (not for kOIMAGEfmtSVG). The parameter is a row variable with the following parameters: 

```
row(cIconID,[ixSize=15,ixBorder=2,ixForeColor=kColorBlack,ixBackColor=kColorWhite])
```

By default, the row requires a single parameter, **cIconID,** which is the icon to be overlaid in the center of the QR code (this can be an SVG or PNG icon image). The second parameter **ixSize** controls the size of the icon, which is a percentage of the output QR image size; this defaults to 15% with a maximum value of 30% (a value over 30% may result in an error). 

A border can be added to the overlaid icon using a third parameter **ixBorder** which defaults to 2 pixels. In addition, you can control the center icon area color, and icon color using parameters **ixForeColor** and **ixBackColor,** which default to black and white (to match the resulting QR image which is black and white). 

For example, to add the account_box icon to the center of a QR code using the default size and border, use the following command: 

96 



## `Do OIMAGE.$makeqrcode(` 

```
lText,iPicture,kOIMAGEfmtPNG,256,
```

```
iErrorLevel,4,errText,row('account_box’))
```

To set the size of the overlaid icon to 25% of the QR image size, add a 5 pixel border, and to set the colors of the overlaid icon and border color, use the following command: 

## `Do OIMAGE.$makeqrcode(` 

```
lText,iPicture,kOIMAGEfmtPNG,256,
```

```
iErrorLevel,4,errText,row('account_box’,25,5,kWhite,kRed))
```

Note the account_box icon is a themed icon so you can set the icon color (but remember the output QR image must be a PNG, i.e. kOIMAGEfmtPNG). 

## **OIMAGE.$resize()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_OIMAGE_|NO|All|



## **Syntax** 

**OIMAGE.$resize** ( _xImage, iWidth, iHeight, &xNewImage_ [, _wParams_ =#NULL, &cErrorText]) 

## **Description** 

Resizes the image _xImage_ to the dimensions supplied in _iWidth_ by _iHeight_ . Returns Boolean true and _xNewImage_ for success, or false and _cErrorText_ if an error occurs. 

_xImage_ and _xNewImage_ are both binary variables. xImage must be a JPEG or PNG image. xNewImage has the same type as xImage. You can use the same binary variable for both parameters if you want to replace the original image. 

_iWidth_ and _iHeight_ can both be greater than zero and less than or equal to 32000, meaning resize to exactly that size. Alternatively, only one of the new dimensions can be zero, meaning calculate the dimension with value zero using the aspect ratio of the input image. 

_wParams_ is an optional row variable of parameters. The following columns can be specified in wParams: 

## 1. **sampler** 

The sampling method to be used when resizing. Either kOIMAGEsamplerBilinear or kOIMAGEsamplerNearestNeighbour. Defaults to kOIMAGEsamplerBilinear if this column is not present, or if wParams is omitted. 

## 2. **gray** 

A Boolean that indicates if the new image is to be a grayscale image. Defaults to kFalse if this column is not present, or if wParams is omitted. 

## 3. **quality** 

If the input image type is JPEG this column contains the JPEG image quality (1 to 100) of the new image. Defaults to 80 if this column is not present, or if wParams is omitted. 

_cErrorText_ The error text returned from the function. 

## **OIMAGE.$transform()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_OIMAGE_|NO|All|



97 



## **Syntax** 

**OIMAGE.$transform** ( _xImage_ , _&xNewImage_ [, _wParams_ =#NULL, _&cErrorText_ ]) 

## **Description** 

Perform a transformation on the image _xImage_ . Returns Boolean true and _xNewImage_ for success, or false and _cErrorText_ if an error occurs. 

_xImage_ and _xNewImage_ are both binary variables. xImage must be a JPEG or PNG image. xNewImage has the same type as xImage. You can use the same binary variable for both parameters if you want to replace the original image. 

_wParams_ is an optional row variable of parameters. The following columns can be specified in wParams: 

## 1. **transform** 

The transformation to be performed, a kOIMAGEtransform… constant, see below. Defaults to kOIMAGEtransformRotate90 if this column is not present, or if wParams is omitted. 

## 2. **quality** 

If the input image type is JPEG this column contains the JPEG image quality (1 to 100) of the new image. Defaults to 80 if this column is not present, or if wParams is omitted. 

Valid transformations are: 

|Constant|Description|
|---|---|
|kOIMAGEtransformRotate90|Rotates the image 90 degrees clockwise; the default|
|kOIMAGEtransformRotate180|Rotates the image 180 degrees|
|kOIMAGEtransformRotate270|Rotates the image 270 degrees clockwise|
|kOIMAGEtransformFlipLeftRight|Flips the image on the left to right axis|
|kOIMAGEtransformFlipTopBottom|Flips the image on the top to bottom axis|
|kOIMAGEtransformTranspose|Transposes the image, i.e. fips the image along a 45 degree|
||axis, from top-left corner to bottom-right corner|



_cErrorText_ The error text returned from the function. 

## **OJSON.$arrayarraytolist()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_OJSON_|NO|All|



## **Syntax** 

## **OJSON.$arrayarraytolist** ( _vData_ [, _&cErrorText_ ]) 

## **Description** 

Parses vData (binary (UTF8/16/32) or character). vData must be a JSON array of arrays containing members with simple types. Returns a list representing the JSON. Returns NULL and cErrorText for an error. 

This method only works with simple types as array members. $arrayarraytolist requires that each JSON array must have the same number of elements, and each JSON array member at a particular index must be of the same data type. 

$arrayarraytolist allows integer and numeric values in the same column (resulting in a numeric column). 

## **OJSON.$couldbearray()** 

98 



|Function group|Execute on client|Platform(s)|
|---|---|---|
|_OJSON_|NO|All|



## **Syntax** 

**OJSON.$couldbearray** (vData) 

## **Description** 

Returns true if vData (either binary (UTF8/16/32) or character) could possibly be a JSON array because its first character is [. 

## **OJSON.$couldbeobject()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_OJSON_|NO|All|



## **Syntax** 

**OJSON.$couldbeobject** (vData) 

## **Description** 

Returns true if vData (either binary (UTF8/16/32) or character) could possibly be a JSON object because its first character is {. 

## **OJSON.$formatjson()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_OJSON_|NO|All|



## **Syntax** 

OJSON.$formatjson( _vData_ ) 

## **Description** 

Parses the JSON in _vData_ (either binary (UTF8/16/32) or character) and returns a formatted representation (or error message if parsing fails) suitable for use in a multi-line entry control. 

## **OJSON.$jsontolistorrow()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_OJSON_|NO|All|



## **Syntax** 

## **OJSON.$jsontolistorrow** ( _vData,[&cErrorText]_ ) 

## **Description** 

Parses the JSON array or object in _vData_ (either binary (UTF8/16/32) or character) and returns a row or a list representing the JSON.Returns NULL and cErrorText if an error occurs. 

99 



## **OJSON.$listorrowtojson()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_OJSON_|NO|All|



## **Syntax** 

**OJSON.$listorrowtojson** (vListOrRow,[iEncoding=kUniTypeUTF8,&cErrorText]) 

## **Description** 

Writes the list or row and returns JSON with the specified encoding (UTF8,UTF16BE/LE,UTF32BE/LE or Character).Returns NULL and cErrorText if an error occurs. 

## **OJSON.$listtoarrayarray()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_OJSON_|NO|All|



## **Syntax** 

## **OJSON.$listtoarrayarray** ( _lList_ [, _iEncoding_ =kUniTypeUTF8 _,&cErrorText_ ]) 

## **Description** 

Writes a list with simple columns to an array of arrays; returns the JSON with specified encoding (UTF8, UTF16BE/LE, UTF32BE/LE or Character). Returns NULL and cErrorText for an error. 

This method only works with simple types as array members. 

## **OJSON.$listtoobjectarray()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_OJSON_|NO|All|



## **Syntax** 

## **OJSON.$listtoobjectarray** ( _lList_ [, _iEncoding_ =kUniTypeUTF8, _&cErrorText_ ]) 

## **Description** 

Writes a list with simple columns to an array of objects; returns JSON with specified encoding (UTF8,UTF16BE/LE,UTF32BE/LE or Character). Returns NULL and cErrorText for an error. 

## **OJSON.$objectarraytolist()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_OJSON_|NO|All|



## **Syntax** 

**OJSON.$objectarraytolist** ( _vData_ [, _&cErrorText_ ]) 

100 



## **Description** 

Parses vData (binary (UTF8/16/32) or character). vData must be a JSON array of objects containing members with simple types. Returns a list representing JSON. Returns NULL and cErrorText for an error. 

## **OmnisICalendar.$createcomponent()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_OmnisICalendar_|NO|All|



## **Syntax** 

## **OmnisICalendar.$createcomponent** ( _iType_ ) 

## **Description** 

Creates a new iCalendar Component object using one of the kICalendarComponent… constants. Returns an iCalendar component object. 

iType: A kICalendarComponent… constant to specify the Component type. 

## **OmnisICalendar.$createrow()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_OmnisICalendar_|NO|All|



## **Syntax** 

## **OmnisICalendar.$createrow** ( _iType_ ) 

## **Description** 

Returns a row which can be used to add or update certain Properties. iType can be one of the kICalendarRowType… constants. 

iType: A kICalendarRowType… constant to specify the type of row. 

## **OmnisIcn Library.$getmask()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_OmnisIcn Library_|NO|All|



## **Syntax** 

**OmnisIcn Library.$getmask** ( _iconid_ [ _,noscale_ ]) 

## **Description** 

Returns a picture variable containing the mask for the icon identified by _iconid_ . 

When noscale is kTrue, a standard resolution image is returned. The default is kFalse, when the parameter is omitted, which will return an image scaled to match the resolution of the current or main display. 

## **Example** 

```
Calculate lPicture as OmnisIcn Library.$getmask(2003)
```

101 



**OmnisIcn Library.$getpict()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_OmnisIcn Library_|NO|All|



## **Syntax** 

**OmnisIcn Library.$getpict** ( _iconid,backgroundcolor_ [, _noscale_ ]) 

## **Description** 

Returns a picture variable containing the icon identified by _iconid_ , drawn on the specified _backgroundcolor_ . 

When noscale is kTrue, a standard resolution image is returned. The default is kFalse, when the parameter is omitted, which will return an image scaled to match the resolution of the current or main display. 

## **Example** 

```
Calculate lPicture as OmnisIcn Library.$getpict(2003,kRed)
```

## **Omnis PDF Device.$encrypt()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Omnis PDF Device_|NO|All|



## **Syntax** 

## **Omnis PDF Device.$encrypt** ( 

cUserPwdASCII[,cOwnerPwdASCII=”,bCanPrint=kTrue,bCanModify=kFalse,bCanCopy=kTrue,bCanAnnotate=kFalse]) 

## **Description** 

Specifies how PDF documents created by the current task will be encrypted. Empty user password disables all encryption options. 

## **Omnis PDF Device.$setdocinfo()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Omnis PDF Device_|NO|All|



## **Syntax** 

**Omnis PDF Device.$setdocinfo** (cAuthor[,cTitle=‘’,cSubject=”]) 

## **Description** 

Sets the document information properties for PDF documents created by the current task. 

## **Omnis PDF Device.$settemp()** 

102 



Function group Execute on client Platform(s) _Omnis PDF Device_ NO All 

## **Syntax** 

Omnis PDF Device.$settemp( _bTemp[,iTimeout]_ ) 

## **Description** 

_bTemp_ false means use $prefs.$reportfile. _bTemp_ true means next PDF is output to temp storage and is valid for _iTimeout_ minutes; returns id to use with PDF $clientcommands.$settemp can be used for each task instance. 

## **omnistoiso8601()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|upto 35924 Date and Time|NO|All|
|asof 35925 Date and Time|YES|All|



## **Syntax** 

**omnistoiso8601** ( _domnisdatetime,bneedtime_ [ _,cerrtext, bMillis=kFalse_ ]) 

## **Description** 

Converts dOmnisDateTime (in UTC) to ISO8601 date/date-time (depends on bNeedTime) and returns it. Returns NULL and cErrText on error. Rounds down hundredths if bMillis is false. 

Hundredths are always rounded down to the nearest tenth. omnistoiso8601() always outputs the timezone using the “Z” UTC time indicator. 

## **ONOTIFY.$removebadge()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_ONOTIFY_|NO|All|



## **Syntax** 

## **ONOTIFY.$removebadge** ( _[,_ & _cErrorText_ ]) 

## **Description** 

Removes the badge from the application icon. Returns Boolean true for success, or false (and sets _cErrorText_ ) if an error occurs. 

## **ONOTIFY.$removelocal()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_ONOTIFY_|NO|All|



## **Syntax** 

**ONOTIFY.$removelocal** ( _[vIDs,_ & _cErrorText_ ]) 

103 



## **Description** 

Removes local notifications with id(s) specified by _vIDs_ which is a single character id, or a single column list of ids (remove all local notifications if _vIDs_ is empty or omitted). Returns Boolean true for success, or false (and _cErrorText_ ) if an error occurs. 

## **ONOTIFY.$sendlocal()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_ONOTIFY_|NO|All|



## **Syntax** 

**ONOTIFY.$sendlocal** ( _cTitle,cMessage,vImage,iAction,wUserInfo,_ [ _iDelay_ =0, _&cErrorText_ ]) 

## **Description** 

Sends a local operating system notification. Returns character notification id for success or returns #NULL (and cErrorText) if an error occurs. 

If the call to $sendlocal() succeeds, it returns a character string. This is a string that uniquely identifies the notification. You can use this string to remove the notification from the system Notification Center using $removelocal, if for example the notification is no longer relevant. 

The parameters are as follows: 

|Parameter|Description|
|---|---|
|_cTitle_|The title of the notifcation. Some text, displayed in|
||bold font above the main notifcation text. The|
||operating system will truncate this if it is too long.|
||Windows allows this to occupy two lines, if you|
||separate the lines using either kCr, lLf or kCr kLf.|
||macOS only allows a single line|
|_cMessage_|The text of the notifcation. This is the main|
||notifcation message, displayed in a plain font. The|
||operating system will truncate this if it occupies|
||more than 4 lines, either due to word wrapping, or|
||the presence of newline characters (kCr, lLf or kCr|
||kLf)|
|_vImage_|Image(s) to be displayed with the notifcation. See|
||the ‘Specifying Images’ section|
|_iAction_|A value that specifes up to 2 optional actions that|
||are to be included in the notifcation; on Windows,|
||this is via one or two buttons; on macOS, this is|
||either via a button for a single action, or via an|
||options popup for two actions. A ‘Specifying|
||Actions’ section|
|_wUserInfo_|A row containing user information that is passed to|
||the $localnotify() method when the user clicks on|
||the notifcation or a notifcation action. It must be|
||possible to convert $userinfo to JSON. See section|
||‘Handling Notifcation Clicks’|
|_iDelay_|The delay in seconds between the call to|
||$sendlocal() and the notifcation being delivered|
||(optional). Omnis can quit before the notifcation is|
||delivered, as the operating system takes care of|
||deferred delivery|
|_cErrorText_|A character variable that receives text describing an|
||error if $sendlocal() fails|



104 



## **ONOTIFY.$setbadgecount()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_ONOTIFY_|NO|All|



## **Syntax** 

**ONOTIFY.$setbadgecount** ( _iCount_ [, _&cErrorText_ , _iBadgeColor_ , _iBadgeTextColor_ ]) 

## **Description** 

Sets the badge on the application icon to have the value _iCount_ . Returns Boolean true for success, or false (and _cErrorText_ ) if an error occurs. 

The parameters are as follows: 

|Parameter|Description|
|---|---|
|_iCount_|The count to display as the badge. Must be greater than|
||zero. When running on Windows, a value greater than|
||99 is displayed as 99+.|
|_cErrorText_|A character variable that receives text describing an|
||error, if $setbadgecount() fails|
|_iBadgeColor_|Windows only. The background color of the count|
||badge. Defaults to styledbadgebackgroundcolor in the|
||“system” section of appearance.json.|
|_iBadgeTextColor_|Windows only. The text color of the count badge.|
||Defaults to styledbadgetextcolor in the “system” section|
||of appearance.json.|



## **ONOTIFY.$setbadgeicon()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_ONOTIFY_|NO|All|



## **Syntax** 

**ONOTIFY.$setbadgeicon** ( _vIconId_ [, _&cErrorText_ , _iBadgeColor_ ]) 

## **Description** 

Note this is available on Windows only. Sets the badge on the application icon to be the specified icon _vIconId_ . Returns Boolean true for success, or false (and sets _cErrorText_ ) if an error occurs. 

The parameters are as follows: 

|Parameter|Description|
|---|---|
|_vIconId_|The icon id of the icon to display as the badge. The size component is ignored, as badges are always 16x16.|
|_cErrorText_|A character variable that receives text describing an error, if $setbadgeicon() fails|
|_iBadgeColor_|The color to be applied to the themed SVG; only applies if the icon is a themed SVG. Default is kColorHilight.|



## **ord()** 

105 



|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Unicode_|NO|All|



## **Syntax** 

**ord** ( _integer_ [, _locale_ , _thousands_ =kfalse]) 

## **Description** 

Returns string comprising positive _integer_ with ordinal suffix for supplied _locale_ , or current language if _locale_ parameter is omitted or empty. Optionally includes ICU _thousands_ separators. 

## **OW3.$computername()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_OW3_|NO|All|



## **Syntax** 

**OW3.$computername** ( _bFormat_ =kFalse) 

## **Description** 

Returns the name of the current computer or an empty string if the name could not be obtained. If _bFormat_ is true, $computername attempts to format the string to make it suitable for an end-user, by removing a ‘.local’ suffix, replacing all - characters with space, and capitalizing each word. 

## **OW3.$escapeuritext()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_OW3_|NO|All|



## **Syntax** 

OW3.$escapeuritext(cTextToEscape) 

## **Description** 

Returns the escaped form of cTextToEscape. All characters except a-z, A-Z, 0-9, - (hyphen), . (period), _ (underscore), and ~ (tilde) are escaped as %hh. Unicode characters are the escaped form of their UTF-8 representation. 

## **OW3.$gethardwareid()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_OW3_|NO|All|



## **Syntax** 

OW3.$gethardwareid() 

106 



## **Description** 

Returns a string ID that identifies the hardware on which Omnis is currently running. This function replaces sys(227) which has been removed. 

## **OW3.$makeuri()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_OW3_|NO|All|



## **Syntax** 

OW3.$makeuri(cURIBase,lParameters) 

## **Description** 

Returns the URI formed by adding the parameters in lParameters to cURIBase, escaping parameter names and values as necessary. lParameters is a list: column 1 is the parameter name and column 2 the parameter value. 

## **OW3.$makeuuid()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_OW3_|NO|All|



## **Syntax** 

OW3.$makeuuid([bIncludeMinusSeparators=kTrue]) 

## **Description** 

Returns a new UUID as a string. bIncludeMinusSeparators affects the format of the returned string: if true, the returned UUID string is 36 characters long and includes – (hyphen) separators (so it has the standard 8-4-4-4-12 format); if false, the returned UUID string is 32 characters long and has no separators. 

## **OW3.$parserfc3339()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_OW3_|NO|All|



## **Syntax** 

**OW3.$parserfc3339** ( _cRfc3339_ [, _bUTC_ =kTrue, _&iOffset_ , _&cErrorText_ ]) 

## **Description** 

Parses a date and time value conforming to RFC3339 and returns an Omnis date-time value and optionally the time zone offset in minutes. Returns #NULL if the string cannot be parsed. 

The parameters are: 

|Parameter|Description|
|---|---|
|_cRfc3339_|a date and time string conforming to RFC3339|
|_bUTC_|If true, the returned date-time value is in UTC rather than the local time zone of the RFC3339 date-time value|



107 



|Parameter|Description|
|---|---|
|_iOffset_|If the RFC3339 date and time string is parsed successfully this receives the time zone offset in minutes|
|_cErrorText_|If supplied, receives text describing the error that caused $parserfc3339 to return #NULL|



## **OW3.$splitmultipart()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_OW3_|NO|All|



## **Syntax** 

**OW3.$splitmultipart** ( _cContentType_ , _xContent_ , _&lMIMEList_ [, _iDefCharSet_ =kUniTypeUTF8, _&cErrorText_ ]) 

## **Description** 

Splits MIME-encoded multi-part _xContent_ into _lMIMEList_ . _cContentType_ must include a boundary parameter. Returns true if successful. The parameters are: 

|Parameter|Description|
|---|---|
|_cContentType_|The content type header (must contain a boundary|
||parameter)|
|_xContent_|The binary content to split|
|_lMIMEList_|Receives the MIME list created by splitting the|
||MIME content. See the documentation for the|
||MailSplit command to see how a MIME list is|
||structured; however note that the charset in the|
||OW3 MIME list is a kUniType… constant|
|_iDefCharSet_|The default character set used to convert character|
||data when there is no charset specifed for a MIME|
||text body part. A kUniType… constant (not|
||Character/Auto/Binary)|
|_&cErrorText_|If supplied, receives text describing the error that|
||caused $splitmultipart to return false|



The MIME list (for this call and for the other OW3 calls that generate a MIME list) now contains an additional column named bodypartheaders. This is a row containing a column for each non-empty header present for the body part. In addition, it has a column named “name” which contains the content-disposition header name parameter. All header names are normalized in the same way as those passed to RESTful services, that is, lower-case with any - characters removed. 

## **OW3.$totpgenerate()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_OW3_|NO|All|



## **Syntax** 

**OW3.$totpgenerate** ( _xSharedSecretKey,iTimeStep,iDigits,&iTOTP_ [, _&cErrorText,iHashType_ =kOW3hashSHA1]) 

108 



## **Description** 

Generates a Time-based One-Time Password in iTOTP using the TOTP algorithm. Returns true if successful. 

_xSharedSecretKey_ (Binary) The shared secret key, length must be between 16 and 256 bytes inclusive. 

_iTimeStep_ (Integer 32 bit) The time step in seconds, must be between 1 and 3600 inclusive. 

_iDigits_ (Integer 32 bit) The number of digits in the TOTP, must be between 6 and 8 inclusive. 

_iTOTP_ (Integer 32 bit) Receives the generated TOTP. 

_cErrorText_ (Character 100000000) If supplied, receives text describing the error that caused $totpgenerate or $totpvalidate to return false. 

_iHashType_ (Integer 32 bit, default is kOW3hashSHA1) The type of hash to use, a kOW3hash… constant. 

See OW3.$totpvalidate(). 

## **OW3.$totpvalidate()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_OW3_|NO|All|



## **Syntax** 

**OW3.$totpvalidate** ( _xSharedSecretKey,iTimeStep,iDigits,iTOTP_ [,& _cErrorText,iHashType_ =kOW3hashSHA1, _iStepsBefore_ =2, _iStepsAfter_ =1]) 

## **Description** 

Validates the Time-based One-Time Password in iTOTP using the TOTP algorithm. Returns true if iTOTP is a valid TOTP. 

_xSharedSecretKey_ (Binary) The shared secret key, length must be between 16 and 256 bytes inclusive. 

_iTimeStep_ (Integer 32 bit) The time step in seconds, must be between 1 and 3600 inclusive. 

_iDigits_ (Integer 32 bit) The number of digits in the TOTP, must be between 6 and 8 inclusive. 

_iTOTP_ (Integer 32 bit) The TOTP that is to be validated. 

_cErrorText_ (Character 100000000) If supplied, receives text describing the error that caused $totpgenerate or $totpvalidate to return false. 

_iHashType_ (Integer 32 bit, default is kOW3hashSHA1) The type of hash to use, a kOW3hash… constant. 

_iStepsBefore_ (Integer 32 bit, default is 2) The number of time steps before the step for the current time that can be checked when validating the supplied TOTP, must be between 1 and 20 inclusive. 

_iStepsAfter_ (Integer 32 bit, default is 1) The number of time steps after the step for the current time that can be checked when validating the supplied TOTP, must be between 1 and 20 inclusive. 

See OW3.$totpgenerate(). 

## **OW3.$unescapeuritext()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_OW3_|NO|All|



## **Syntax** 

OW3.$unescapeuritext(cTextToUnescape) 

109 



## **Description** 

Returns the unescaped form of cTextToUnescape by unescaping %hh sequences and converting the resulting UTF-8 string to character. Returns NULL if the string is not a valid escaped value. 

## **OXML.$base64decode()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_OXML_|NO|All|



## **Syntax** 

**OXML.$base64decode** (cData,&cErrorText) 

## **Description** 

Decodes the BASE64 encoded Binary data in cData and returns the result, or NULL and cErrorText if an error occurs. 

## **OXML.$base64encode()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_OXML_|NO|All|



## **Syntax** 

**OXML.$base64encode** (xData,&cErrorText) 

## **Description** 

Encodes the data using BASE64 and returns the result as a Binary, or NULL and cErrorText if an error occurs. 

## **OXML.$formatbinaschar()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_OXML_|NO|All|



## **Syntax** 

**OXML.$formatbinaschar** (xData[,iBytesPerRow=16,iMaxLength=0]) 

## **Description** 

Formats at most the first iMaxLength bytes of binary data _xData_ into character data suitable for display in a multi-line entry field. 

## **OXML.$maybexml()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_OXML_|NO|All|



## **Syntax** 

**OXML.$maybeXML** ( _xData_ ) 

110 



**Description** 

Returns true if the binary data is likely to be XML (it starts with <?xml, in one of the encodings supported by the parser). 

## **OXML.$md5hexdigest()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_OXML_|NO|All|



## **Syntax** 

## **OXML.$md5hexdigest** ( _cData_ ) 

## **Description** 

Generates an MD5 hex digest based on the supplied character data. 

## **OXML.$striphttpheader()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_OXML_|NO|All|



## **Syntax** 

OXML.$striphttpheader( _&cData_ ) 

## **Description** 

Strips the HTTP header from the argument. 

## **parsehttpauth()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_RESTful_|NO|All|



## **Syntax** 

**parsehttpauth** ( _auth_ ) 

## **Description** 

Parses the HTTP Authorization header value _auth_ and returns a row variable containing the extracted information. Column 1 of the returned row (named scheme) is the scheme (e.g. basic). Other columns are scheme dependent. 

## **parsehttpdate()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_RESTful_|NO|All|



## **Syntax** 

**parsehttpdate** ( _httpdate_ ) 

111 



## **Description** 

Parses date value _httpDate_ in HTTP header format (e.g. Sun, 06 Nov 1994 08:49:37 GMT) and returns an Omnis date-time value (in UTC) or NULL if the value cannot be parsed successfully. 

## **pathsep()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|NO|All|



## **Syntax** 

## **pathsep** () 

## **Description** 

Returns the pathname separator for the current OS. 

## **Example** 

```
Calculate lPathSep as pathsep()
# returns '\' on Windows
# returns '/' on macOS
# returns '/' on Linux
```

## **pday()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Date and Time_|NO|All|



## **Syntax** 

**pday** (datepart,date) 

## **Description** 

Returns the date of the day before the specified _date_ when the _datepart_ constant is set to kDay. 

However, if one of the day of the week constants is used, this function returns the date of that day of the week preceding the specified _date_ . 

The datepart constants that you can use are: kDay, kSunday, kMonday, kTuesday, kWednesday, kThursday, kFriday, kSaturday. 

## **Example** 

```
Calculate lDate as pday(kDay,#D)
```

```
# returns May 7 2003, assume #D is May 8, 2003
```

```
Calculate lDate as pday(kThursday,#D)
```

```
# returns May 1 2003, which is the Thursday before #D, assume #D is May 8, 2003
```

## **pick()** 

112 



|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Lookup_|YES|All|



## **Syntax** 

**pick** (number,value0,value1[,value2]…) 

## **Description** 

Selects an item from a list of _values_ (strings or numbers) using _number_ as a zero-based index and returns the result. 

The _number_ argument is rounded to an integer and used to select the item. _value0_ is returned if the result is 0, _value1_ if the result is 1, _value2_ if the result is 2, and so on. If the _number_ is less than zero or greater than the number of values in the list, an empty value is returned. Note the list of values can be a mixture of string and numeric values. 

## **Example** 

```
Calculate lResult as pick(lVar1,123,'ABC','abc')
# returns 123 if lVar1 evaluates to 0
```

```
Calculate lResult as pick(lVar2,2200,4500,6800)
```

```
# returns 6800 if lVar2 evaluates to 2
```

```
Calculate lResult as pick(lVar3,'one',2,'three')
```

```
# returns empty if lVar3 evaluates to 5
```

## **pictconvfrom()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Picture_|NO|All|



## **Syntax** 

**pictconvfrom** (format,binary-raw-data) 

## **Description** 

pictconvfrom() takes the _binary-raw-data_ in the specified _format_ and returns a value suitable for use in relevant Omnis fields. Typically this means that pictconvfrom() adds header information to raw data. 

Valid values for the format are as follows: 

## • **CS24** 

Omnis color shared picture format (16 million colors), including the internal Omnis header. 

- **PNG** 

PNG (Portable Network Graphics) format (Raw, as written on disk) 

## • **JPEG** 

JPEG format (Raw, as written on disk) 

In addition, it is possible to add further formats using the external component interface. 

The following example reads a JPEG file from disk and displays it. 

113 



**Example** 

```
ReadBinFile ("c:\myfile.jpg",lJpegData)
Do pictconvfrom("jpeg",lJpegData) Returns lJpegData
# converts the JPEG data lJpegData into a suitable value for Omnis fields
```

## **pictconvto()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Picture_|NO|All|



## **Syntax** 

**pictconvto** (source-format,source-data,dest-format) 

## **Description** 

Converts the binary _source-data_ (with or without our internal header) from the _source-format_ to the _dest-format_ ,and returns the resulting binary value. 

On macOS, conversion supports all bitmap data formats, including PNG, TIFF, BMP, JPEG, and GIF. Where a source data format is empty, an attempt will be made to convert from any supported bitmap image representation. In this case, the data must be in raw format with no Omnis header. 

See _pictconvfrom()_ for details of possible formats. 

The following example converts the PNG data in lPngData to JPEG. 

## **Example** 

```
Do pictconvto("png",lPngData,"jpeg") Returns lJpegData
# converts the PNG data in lPcxData to JPEG
```

## **pictconvtypes()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Picture_|NO|All|



## **Syntax** 

**pictconvtypes** () 

## **Description** 

Returns a single column list, which contains all the picture conversion format types registered with Omnis. 

## **Example** 

```
Calculate lTypes as pictconvtypes()
# returns a list containing all the picture conversion types
```

## **pictformat()** 

114 



|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Picture_|NO|All|



## **Syntax** 

**pictformat** ( _source-data_ ) 

## **Description** 

Returns a character string which indicates the picture format of the binary _source-data_ . See _pictconvfrom_ () for details of possible formats. 

Note that there are certain formats that **pictformat()** cannot recognize (for example, OLE data, GIF), and in these cases, **pictformat()** returns an empty string. 

## **Example** 

```
Calculate lFormat as pictformat(lJpegData)
# returns "JPEG"
```

## **pictsize()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Picture_|NO|All|



## **Syntax** 

**pictsize** (source-data,width,height) 

## **Description** 

Sets _width_ and _height_ to the width and height of the picture stored in the supplied binary or picture _source-data_ . 

If the function fails, for example because it cannot recognize the format of the data, then width and height will be zero. 

## **Example** 

```
Do pictsize(lJpegData,lWidth,lHeight)
# returns the width and height of lJpegData
```

## **platform()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|NO|All|



## **Syntax** 

**platform** () 

## **Description** 

Returns the OS code for the current Omnis executable. 

115 



## **Example** 

```
Calculate lPlatform as platform()
# returns 'N' on Windows NT/2000/2003/XP/Vista/Win7/8/10
```

```
# returns 'X' on macOS
```

```
# returns 'U' on Linux
# returns 'W' on Windows 95/98/ME ## deprecated
```

## **PortProfile.$getportnames()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_PortProfle_|NO|All|



## **Syntax PortProfile.$getportnames** ( _list-of-names_ ) **Description** Populates _list-of-names_ with a list of all available ports on the current platform. 

## **Example** 

`Do PortProfile.$getportnames(lPorts)` **PortProfile.$getprofilenames()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_PortProfle_|NO|All|
|**Syntax**|||
|**PortProfle.$getproflenames**(_list-of-names_)|||
|**Description**|||
|Populates_list-of-names_with a list of all profle names currently defned.|||
|**Example**|||



## `Do PortProfile.$getprofilenames(lPorts)` 

## **pos()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_String_|YES|All|
|**Syntax**|||



**pos** (substring,string) 

116 



## **Description** 

Returns the position of _substring_ in _string_ , or zero if _substring_ is not contained in _string_ . 

The _substring_ must be contained within _string_ in its entirety for the returned value to be non-zero. Also, the comparison is case sensitive and only the first occurrence of _substring_ is returned (see third example). 

## **Example** 

```
Calculate lResult as pos('Mouse','Mickey Mouse')
```

```
# returns 8
```

```
Calculate lResult as pos('mouse','Mickey Mouse')
```

```
# return 0, note case
```

```
Calculate lResult as pos(' ','R S W Smith')
```

```
# returns 2, that is the position of the first space character
```

```
# you can strip the extension from a filename using mid() and pos() combined
If pos('.',lFileName) ## if lFileName contains a dot
```

```
Calculate lFileName as mid(lFileName,1,pos('.',lFileName)-1)
```

```
End If
```

## **prinf()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|YES|macOS and Linux|



## **Syntax** 

**printf** (string[,newline=ktrue]) 

## **Description** 

Writes the string to standard output followed by a newline character if required (the function is ignored on Windows. Executes on macOS and Linux only). 

## **putenv()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|NO|All|



## **Syntax** 

**putenv** (name,value) 

## **Description** 

Sets the Omnis process environment variable with the specified _name_ to the specified _value_ ; creates a new environment variable if necessary; returns Boolean true for success, false for failure. 

## **Example** 

```
# Set the environment variable MYVAR to the value MYVALUE
Do putenv("MYVAR","MYVALUE")
```

117 



## **pwr()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Number_|YES|All|



## **Syntax** 

**pwr** (number,power) 

## **Description** 

Returns the result of raising a _number_ to a _power_ . 

## **Example** 

```
Calculate lResult as pwr(2,5)
# returns 32
Calculate lResult as pwr(21.37,0.831)
# returns 12.74 approx
Calculate lResult as int(pwr(1.105,5))
# is the same as int(1.65) which returns 1
```

## **rand()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Random_|NO|All|



## **Syntax** 

**rand** () 

## **Description** 

Returns a random real number in the range 0.0 < number < 1.0, inclusive (note no argument). 

## **Example** 

```
Calculate lResult as rand()
```

## **randintrng()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Random_|NO|All|



## **Syntax** 

**randintrng** (number1,number2) 

118 



## **Description** 

Returns a random integer between _number1_ and _number2_ inclusive. 

## **Example** 

```
Calculate lResult as randintrng(25,50)
```

## **randrealrng()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Random_|NO|All|



## **Syntax** 

**randrealrng** (number1,number2) 

## **Description** 

Returns a random real number between _number1_ and _number2_ inclusive. 

## **Example** 

```
Calculate lResult as randrealrng(25,50)
```

## **rcedit.$setapplicationmanifest()** 

**==> picture [206 x 24] intentionally omitted <==**

**----- Start of picture text -----**<br>
Function group Execute on client Platform(s)<br>rcedit NO All<br>**----- End of picture text -----**<br>


## **Syntax** 

**rcedit.$setApplicationManifest** ( _cFileName_ , _cManifestPath_ ) 

## **Description** 

Sets manifest from file path in _cManifestPath_ to exe/dll in _cFileName_ . Returns kTrue if operation succeeded, else kFalse. 

## **rcedit.$setfileversion()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|rcedit|NO|All|



## **Syntax** 

**rcedit.$setFileVersion** ( _cFileName_ , _cFileVersion_ ) 

## **Description** 

Sets file version to value from _cFileVersion_ to exe/dll in _cFileName_ . Returns kTrue if operation succeeded, else kFalse. 

119 



## **rcedit.$seticon()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|rcedit|NO|All|



## **Syntax** 

## **rcedit.$setIcon** ( _cFileName_ , _cIcoPath_ ) 

## **Description** 

Sets icon to exe/dll in _cFileName_ using filepath to .ico in _cIcoPath_ . Returns kTrue if operation succeeded, else kFalse. 

## **rcedit.$setproductversion()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|rcedit|NO|All|



## **Syntax** 

**rcedit.$setProductVersion** ( _cFileName_ , _cProductVersion_ ) 

## **Description** 

Sets product version to value from _cProductVersion_ to exe/dll in _cFileName_ . Returns kTrue if operation succeeded, else kFalse. 

## **rcedit.$setresourcestring()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|rcedit|NO|All|



## **Syntax** 

**rcedit.$setResourceString** ( _cFileName_ , _cKey, cValue_ ) 

## **Description** 

Sets the resource string with key _cKey_ to value _cValue_ to exe/dll in _cFileName_ . Returns kTrue if operation succeeded, else kFalse. 

## **rcedit.$setversionstring()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|rcedit|NO|All|



## **Syntax** 

**rcedit.$setVersionString** ( _cFileName_ , _cKey, cValue_ ) 

## **Description** 

Sets version string with key _cKey_ to value _cValue_ to exe/dll in _cFileName_ . Returns kTrue if operation succeeded, else kFalse. 

120 



**replace()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_String_|YES|All|



## **Syntax** 

**replace** (source-string,target-string,replacement-string) 

## **Description** 

Replaces the first occurrence of the _target-string_ , within the _source-string_ , with the _replacement-string_ . Returns the resulting string. 

## **Example** 

```
Calculate lString as replace('admInIstratIon',chr(73),'i')
# returns 'adminIstratIon'
```

## **replaceall()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_String_|YES|All|



## **Syntax** 

**replaceall** (source-string,target-string,replacement-string) 

## **Description** 

Replaces all occurrences of the _target-string_ , within the _source-string_ , with the _replacement-string_ . Returns the resulting string. 

## **Example** 

```
Calculate lString as replaceall('admInIstratIon',chr(73),'i')
# returns 'administration'
```

## **rgb()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|YES|All|



## **Syntax** 

**rgb** (red,green,blue) 

## **Description** 

Returns the RGB value formed from the 3 supplied color components (each of which must be 0-255). 

The three arguments _red, green, blue_ correspond to the RGB value of the desired color; each must be an integer in the range 0-255. For example, yellow has an RGB value of 255,255,0. 

See also rgba(). 

121 



## **Example** 

```
Do $cinst.$objs.FIELD1.$forecolor.$assign(rgb(0,178,178))
# changes the object forecolor to green
```

## **rgba()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|YES|All|



## **Syntax** 

**rgba** (red,green,blue,alpha) 

or **rgba** (constant,alpha) 

## **Description** 

Returns the RGBA value formed from the 3 supplied color components (each of which must be 0-255) and an alpha component (0-255), where 255 is fully opaque. Alternatively, a color constant and an alpha value can be supplied. 

The four arguments _red, green, blue, alpha_ correspond to the RGBA value of the desired color; each must be an integer in the range 0-255. 

The return value can be assigned to an RGBA color property, but only where a color _and_ alpha value is required. 

See also rgb(). 

## **Example** 

```
Do $cinst.$objs.FIELD1.$examplecolor.$assign(rgb(0,178,178,127))
```

```
# changes the object color to green with 50% opacity
```

```
Do $cinst.$objs.FIELD1.$examplecolor.$assign(rgb(kRed,192))
```

```
# changes the object color to red with 75% opacity
```

## **right()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_String_|YES|All|



## **Syntax** 

**right** (string,n) 

## **Description** 

Returns the substring comprising the last _n_ characters of the _string_ . 

## **Example** 

```
Calculate lResult as right('Elephant',3)
# returns 'ant'
```

122 



**rmousedn()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Mouse_|NO|All|



## **Syntax** 

**rmousedn** () 

## **Description** 

Returns true if the right mouse button is held down (under Windows and Linux), or the Ctrl key is held down while the mouse/pointer is clicked (under macOS). If rmousedn() is true, _mousedn_ () is also true but not vice versa (note no argument). 

_Note: This function is for desktop apps using Window classes only, not web or mobile apps._ 

## **rmouseup()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Mouse_|NO|All|



## **Syntax** 

**rmouseup** () 

## **Description** 

Returns true if, after being pressed, the right mouse button is up (under Windows and Linux) or the mouse is up after the mouse/pointer has been pressed with the Ctrl key held down (under macOS) (note no argument required). 

_Note: This function is for desktop apps using Window classes only, not web or mobile apps._ 

## **rnd()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Number_|YES|All|



## **Syntax** 

**rnd** (number,dp) 

**rnd** (number,dp[,asnumber=kfalse]) 

## **Description** 

Rounds a _number_ to a number of decimal places specified in _dp_ and returns the result. 

Rounds a _number_ to a number of decimal places specified in _dp_ and returns the result as a string, or a number if _asnumber_ is kTrue. 

Note that the return value of **rnd()** is (by default) a character string. This is the only representation of the returned number guaranteed to hold the result correctly, due to potential floating point inaccuracies. 

You need to be careful when comparing the return values of two calls to **rnd()** , since the return values are character strings, and will be compared as strings. 

The optional parameter _asnumber_ allows you to specify that the function should return a Number, rather than a Character value. Note that this may lose some precision if the data type cannot represent the full floating point value. 

123 



## **Example** 

```
Calculate lResult as rnd(2.105693,5)
# returns 2.10569
```

```
Calculate lResult as rnd(2.105693,3)
```

```
# returns 2.106
```

```
Calculate lResult as rnd(0.5,0)
# returns 1
```

## **rolldice()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Random_|NO|All|



## **Syntax** 

**rolldice** (number,faces) 

## **Description** 

Returns the result of a die roll. You specify the _number_ of dice to roll and the number of _faces_ on each die. 

## **Example** 

```
Calculate lResult as rolldice(2,6)
```

```
# “rolls” two normal, six-sided dice and puts the result in lResult
```

## **rollstring()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Random_|NO|All|



## **Syntax** 

**rollstring** (string-formula) 

## **Description** 

Returns the result of a die roll from a _string-formula_ . 

The format of the _string-formula_ is: 

rollstring NdF [ + - * / offset ] 

where N is the number of dice, d is a delimiter, and F is the number of faces for each die. In addition, you can add, subtract, multiply, or divide by an offset. 

## **Example** 

```
Calculate lResult as rollstring('2d6')
```

```
# returns the result of rolling two standard sixed-faced dice
```

```
Calculate lResult as rollstring('3d6+1')
```

```
Calculate lResult as rollstring('12d4+6')
```

124 



**row()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_List_|YES|All|



## **Syntax** 

**row** (expression1[,expression2]…) 

## **Description** 

Creates and returns a row with a column for each parameter set to the value of the supplied _expression_ . When a parameter is a variable, the column is named using the variable name: see the example. 

## **Example** 

```
Calculate lRow1 as row(lVar1,lVar2,lVar3)
```

```
# creates a row variable with the column names lVar1, lVar2, lVar3
```

## **rpos()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_String_|YES|All|



## **Syntax** 

**rpos** (substring,string) 

## **Description** 

Returns the position of the last occurrence of _substring_ in _string_ , or zero if _substring_ is not contained in _string._ 

The _substring_ must be contained within _string_ in its entirety for the returned value to be non-zero. Also, the comparison is case sensitive. 

## **Example** 

```
Calculate lResult as rpos('Mouse','Mickey Mouse')
```

```
; returns 8
```

```
Calculate lResult as rpos('mouse','Mickey Mouse')
; return 0, note case
```

```
Calculate lResult as rpos(' ','R S W Smith')
; returns 6, that is the position of the last space character
```

## **rxpos()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_String_|NO|All|



125 



## **Syntax** 

**rxpos** (rx,str,igncase,words,mchlen[,captureRow]) 

## **Description** 

Returns position of characters matching regular expression _rx_ in _str_ , or zero for no match; sets _mchlen_ to length of match. _igncase_ and _words_ are Boolean, true for ignore case or only match whole words. 

The optional parameter captureRow has been added to PCRE2 regular expressions (the default from Studio 10.2). You can pass this a row variable that returns the captured groups resulting from the regular expression match operation. This is a standard feature of regular expressions – groups correspond to the parts of the regular expression contained in parentheses (provided that the open parenthesis is not followed by ?: indicating a non-capturing group). Groups can also optionally be named, and they are numbered 1 to n, with various rules regarding duplication when using the | operator. For example: 

1. When rxpos() locates nothing, it sets captureRow to empty. 

2. When rxpox() locates something, and the captureRow parameter is supplied, it adds a column to the captureRow for each captured group, where the column name is G<n> for group number n where the group is not named, or the group name. 

The following examples will illustrate this: 

```
Calculate cString as "2017-01-02"
```

```
Do rxpos("^(?<year>\d{4})-(?<month>\d{2})-(?<day>\d{2})$",cString,0,0,cLen,cRow) Returns cOffset
```

After executing the above line, cRow is a row with three columns named year, month, and day, with the values 2017, 01 and 02, respectively. 

```
Calculate cString as "hey_test_ho"
```

```
Do rxpos("(hey|ho)_test_(ho|hey)",cString,0,0,cLen,cRow) Returns cOffset
```

After executing the above line, cRow is a row with two columns named G1 and G2, with the values hey and ho. 

You can mix named and unnamed capture groups. 

## **setfye()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Date and Time_|NO|All|



## **Syntax** 

**setfye** ( _date_ ) 

## **Description** 

Sets the _date_ of the fiscal year end. 

The _date_ does not have to be in the current year, that is, the function ignores the year part of the date. The setting of the fiscal year end affects all other date functions that involve quarters. It returns the previous value so you can save it for later use. 

## **Example** 

```
Calculate lDate as setfye('MAR 31')
```

```
# sets the fiscal year end to March 31st
```

```
Calculate lDate as setfye('12 31 03')
```

```
# sets the fiscal year end to December 31st and ignores the year
```

126 



**setseed()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Random_|NO|All|



## **Syntax** 

**setseed** ( _seed_ ) 

## **Description** 

Sets the random number _seed_ for the random functions, such as _rand_ (). setseed() converts _seed_ into a Long number. It returns the previous seed as an integer number. 

## **Example** 

```
Calculate lResult as setseed(10)
```

```
# sets seed to 10 and returns previous seed in lResult
```

## **setws()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Date and Time_|NO|All|



## **Syntax** 

**setws** (datepart) 

## **Description** 

Sets the beginning of the week using one of the day of the week _datepart_ constants, e.g. kSunday. This affects the value returned by the functions dpart(), fday() and lday(). 

It returns the previous value so you can save it for later use. If the _datepart_ is invalid this function still returns the week start but does not change it. 

The datepart constants that you can use are: kSunday, kMonday, kTuesday, kWednesday, kThursday, kFriday, kSaturday. 

## **Example** 

```
Calculate lDate as setws(kMonday)
# sets Monday as the week start
```

## **sha256()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|Binary Field|NO|All|



## **Syntax** 

**sha256** (binary) 

127 



## **Description** 

Returns the 32-byte binary SHA-256 hash of the supplied binary data. Returns #NULL if binary is null or empty. 

## **sha512()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|Binary Field|NO|All|



## **Syntax** 

**sha512** (binary) 

## **Description** 

Returns the 64-byte binary SHA-512 hash of the supplied binary data. Returns #NULL if binary is null or empty. 

## **shift()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|YES|All|



## **Syntax** 

## **shift** () 

## **Description** 

Returns true if the Shift key is being pressed. 

## **shufflelist()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Random_|NO|All|



## **Syntax** 

**shufflelist** (sourcelist,targetlist,number) 

## **Description** 

Shuffles the items in _sourcelist_ , the specified _number_ of times, and puts the results in _targetlist_ . 

A value of 2 or 3 for _number_ provides a good shuffle. **shufflelist()** does not support Binary fields, List fields, and Picture fields stored in a list. An empty or null date converts to ‘31 DEC 00’ in the _targetlist_ . 

## **Example** 

```
Do shufflelist(lSourceList,lTargetList,3)
```

```
# shuffles lSourceList three times and puts the result in lTargetList
```

128 



**sin()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Trigonometric_|YES|All|



## **Syntax** 

**sin** ( _angle_ ) 

## **Description** 

Returns the Sine of an _angle_ where the _angle_ is in degrees (or radians if #RAD is true). 

## **Example** 

```
Calculate lResult as sin(30)
# returns 0.5
```

## **sleep()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|NO|All|



## **Syntax** 

**sleep** (milliseconds) 

## **Description** 

Suspends execution for the specified number of _milliseconds_ ; returns true if execution suspended successfully or false if an error occurred. 

The actual delay can be longer in the multi-threaded server if another stack is executing its time slice when the sleep delay expires. As soon as you execute sleep() in the multi-threaded server, other waiting stacks can run. 

## **split()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_String_|YES|All|



## **Syntax** 

**split** ( _string_ [, _delimiters_ =‘,’, _stripwhitespace_ = _kfalse_ ]) 

**split** ( _string_ [, _delimiters_ = _kComma_ , _stripwhitespace_ = _kfalse_ ]) 

## **Description** 

Splits _string_ at the character(s) in _delimiters_ and returns a list of the resulting substrings. Strips leading and trailing whitespace from each substring if _stripWhitespace_ is kTrue. 

129 



## **sqr()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Number_|YES|All|



## **Syntax** 

**sqr** (number) 

## **Description** 

Returns the square root of a _number_ . Omnis defines the square root of a negative number X as _sqr_ (abs(X)). 

## **Example** 

```
Calculate lResult as sqr(100)
# returns 10
```

```
Calculate lResult as sqr('-301.56')
# returns 17.37 approx
```

```
Calculate lResult as mid('Omnis',sqr(16),2)
# returns 'is'
```

## **startswith()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_String_|YES|All|



## **Syntax** 

**startswith** ( _string_ , _start[,ignorecase=kFalse]_ ) 

## **Description** 

Returns true if the _string_ starts with the non-empty string _start_ . If _ignorecase_ is kTrue, the function uses case-insensitive comparison. 

## **Example** 

```
Calculate lString as 'Fast prototyping'
```

```
If startswith(lString,'Fast')
# returned True
End If
```

```
Calculate lBoolean as startswith(lString,'FAST',kTrue)
# lBoolean = True
```

## **stddevc()** 

130 



|Function group|Execute on client|Platform(s)|
|---|---|---|
|_List_|NO|All|



## **Syntax** 

**stddevc** (listname,column[,ignore-nulls]) 

## **Description** 

Returns the standard deviation for a list column specified by _listname_ and _column_ . stddevc() can only be used with columns defined using variables so it cannot be used with lists defined from a SQL class. 

If you set _ignore_nulls_ to 1, null values are ignored and not counted. If you omit this parameter or it evaluates to zero, nulls are treated as zero values and are counted. 

## **Example** 

```
Calculate lResult as jst(stddevc(lList,lCol1),'N2')
```

```
# returns the standard deviation rounded to 2 decimal places
```

## **stgetcol()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Client String Table_|NO|All|



## **Syntax** 

**stgetcol** ( _table_ ) 

## **Description** 

Returns the name of the current column for string table _table_ (iOS plug-in client methods only). 

## **stgettext()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_StringTable_|YES|All|



## **Syntax** 

**stgettext** ( _id_ ) 

## **Description** 

Returns the string with the _id_ from a string table, or empty if the lookup fails. (Supported in client methods; when using $stringtable in the remote task supported in client and server methods for the task string table). 

## **StringTable.$colcnt()** 

131 



|Function group|Execute on client|Platform(s)|
|---|---|---|
|_StringTable_|NO|All|



## **Syntax** 

**StringTable.$colcnt** ([cTableName]) 

## **Description** 

Returns the number of columns in string table cTableName, or an error code which is less than zero (see the kStringTable… constants). 

## **Example** 

```
Calculate lResult as StringTable.$colcnt('MyStringTable')
# returns the number of columns in MyStringTable
```

## **StringTable.$getcolumnname()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_StringTable_|NO|All|



## **Syntax** 

StringTable.$getcolumnname( _[cTableName]_ ) 

## **Description** 

Returns the current column name for the string table specified by _cTableName_ , or an error code which is less than zero (see the kStringTable… constants). 

## **Example** 

```
Calculate lResult as StringTable.$getcolumnname('MyStringTable')
# returns the name of the current column in MyStringTable
```

## **StringTable.$getcolumnnumber()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_StringTable_|NO|All|



## **Syntax** 

## **StringTable.$getcolumnnumber** ( _[cTableName]_ ) 

## **Description** 

Returns the current column number for the string table specified by _cTableName_ , or an error code which is less than zero (see the kStringTable… constants). 

132 



## **Example** 

```
Calculate lResult as StringTable.$getcolumnnumber('MyStringTable')
# returns the number of the current column in MyStringTable
```

## **StringTable.$getlistfromfile()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_StringTable_|NO|All|



## **Syntax** 

**StringTable.$getlistfromfile** ( _cPathname_ ) 

## **Description** 

Reads the string table file _cPathname_ , and returns the string table list it contains. 

## **StringTable.$gettablelist()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_StringTable_|NO|All|



## **Syntax** 

## **StringTable.$gettablelist** ( _&lList_ ) 

## **Description** 

Populates a two column _lList_ with the loaded string table names in column 1 and their pathnames in column 2. Define lList to have two character columns before calling this method. 

## **Example** 

```
Do StringTable.$gettablelist(lTableList)
# returns a list of all loaded string tables
```

## **StringTable.$gettext()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_StringTable_|NO|All|



## **Syntax** 

StringTable.$gettext( _cRowID_ ) 

## **Description** 

Returns the text for a cell, or an error code less than zero (a kStringTable… constant). _cRowID_ is either the row name within the current column, or when using multiple tables it has the syntax TABLENAME.ROWNAME[.COLUMNNAME]. 

133 



## **Example** 

```
Calculate lResult as StringTable.$gettext('A')
```

```
# returns the text from the cell with id 'A' in the current column
```

## **StringTable.$loadcolumn()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_StringTable_|NO|All|



## **Syntax** 

**StringTable.$loadcolumn** (cColumnNumberOrName,cTableName,cPathname) 

## **Description** 

Loads column _cColumnNumberOrName_ from string table _cPathname_ into table _cTableName_ . Returns kStringTableOK or an error code which is less than zero (see the kStringTable… constants). 

## **Example** 

```
Do StringTable.$loadcolumn(lCol1,lTable,lPath)
```

```
# loads the column lCol1 from the table specified in lPath, into the table lTable
```

## **StringTable.$loadexistingtablefromlist()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_StringTable_|NO|All|



## **Syntax** 

## **StringTable.$loadexistingtablefromlist** ( _cTableName,lList_ ) 

## **Description** 

Replaces an existing string table with the content of a list. Returns kStringTableOK or an error code which is less than zero (see the kStringTable… constants). 

## **StringTable.$loadlistfromtable()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_StringTable_|NO|All|



## **Syntax** 

**StringTable.$loadlistfromtable** ( _cTableName_ ) 

## **Description** 

Copies string table _cTableName_ to a list, and returns the list. 

134 



## **Example** 

```
Calculate lTableList as StringTable.$loadlistfromtable(lTable)
# copies the string table lTable to a list lTableList
```

## **StringTable.$loadstringtable()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_StringTable_|NO|All|



## **Syntax** 

**StringTable.$loadstringtable** ( _cTableName,cPathname_ ) 

## **Description** 

Loads string table from file _cPathname_ , and gives it the name _cTableName_ . Returns kStringTableOK or an error code which is less than zero (see the kStringTable… constants). 

## **Example** 

```
Do StringTable.$loadstringtable(lTable,lPath)
```

```
# loads the table specified in lPath into the table lTable
```

## **StringTable.$loadtablefromlist()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_StringTable_|NO|All|



## **Syntax** 

**StringTable.$loadtablefromlist** ( _cTableName,cPathname,lList_ ) 

## **Description** 

Creates a string table from a list. Returns kStringTableOK or an error code which is less than zero (see the kStringTable… constants). 

## **Example** 

```
Do StringTable.$loadtablefromlist(lTable,lPath,lTableList)
# creates a string table from lTableList
```

## **StringTable.$redraw()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_StringTable_|NO|All|



## **Syntax** 

**StringTable.$redraw** ( _hwnd_ ) 

135 



## **Description** 

Redraws the window specified by _hwnd_ . Returns kStringTableOK or an error code which is less than zero (see the kStringTable… constants). 

## **StringTable.$removestringtable()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_StringTable_|NO|All|



## **Syntax** 

**StringTable.$removestringtable** ( _cPathname_ ) 

## **Description** 

Deletes the string table file specified by _cPathname_ . Returns kStringTableOK or an error code which is less than zero (see the kStringTable… constants). 

## **Example** 

```
Do StringTable.$removestringtable(lPath)
```

```
# removes the string table specified in lPath
```

## **StringTable.$rowcnt()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_StringTable_|NO|All|



## **Syntax** 

**StringTable.$rowcnt** ( _[cTableName]_ ) 

## **Description** 

Returns the number of rows in string table _cTableName_ , or an error code which is less than zero (see the kStringTable… constants). 

## **Example** 

```
Calculate lResult as StringTable.$rowcnt('MyStringTable')
# returns the number of row in MyStringTable
```

## **StringTable.$savestringtable()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_StringTable_|NO|All|



## **Syntax** 

**StringTable.$savestringtable** ( _cTableName_ ) 

136 



## **Description** 

Saves the string table specified by _cTableName_ . Returns kStringTableOK or an error code which is less than zero (see the kStringTable… constants). 

## **Example** 

```
Do StringTable.$savestringtable(lTable)
# saves the string table lTable
```

## **StringTable.$setcolumn()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_StringTable_|NO|All|



## **Syntax** 

**StringTable.$setcolumn** ( _cColumnNumberOrName_ ) 

## **Description** 

Sets the current column (which can be prefixed by ‘TABLENAME.’. Returns kStringTableOK or an error code which is less than zero (see the kStringTable… constants). 

## **Example** 

```
Do StringTable.$setcolumn(lCol1)
```

```
# sets lCol1 as the current column
```

## **StringTable.$unloadall()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_StringTable_|NO|All|



## **Syntax** 

**StringTable.$unloadall** () 

## **Description** 

Unloads all string tables from memory. 

## **Example** 

```
Do StringTable.$unloadall()
# removes all string tables from memory
```

## **StringTable.$unloadstringtable()** 

137 



|Function group|Execute on client|Platform(s)|
|---|---|---|
|_StringTable_|NO|All|



## **Syntax** 

**StringTable.$unloadstringtable** ( _cTableName_ ) 

## **Description** 

Unloads the string table _cTableName_ from memory. Returns kStringTableOK or an error code which is less than zero (see the kStringTable… constants). 

## **Example** 

```
Do StringTable.$unloadstringtable(lTable)
# removes the string table lTable from memory
```

## **Strip()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_External functions_|NO|All|



## **Syntax** 

**Strip** (string,character) 

## **Description** 

Removes all instances of _character_ from _string_ , and returns the resulting string. 

## **Example** 

```
Calculate #S1 as Strip("Sunshine",'n')
# returns "Sushie"
```

## **strpbrk()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_String_|NO|All|



## **Syntax** 

**strpbrk** (string1,string2) 

## **Description** 

Returns the substring of _string1_ from the point where any of the characters in _string2_ match _string1_ . 

## **Example** 

```
Calculate lString as "this is a test"
Calculate lNewString as strpbrk(lString,"absj")
# returns the string "s is a test"
```

138 



**strspn()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_String_|NO|All|



## **Syntax** 

**strspn** (string1,string2) 

## **Description** 

Returns the index of the first character in _string1_ that does not match any of the characters in _string2_ . 

## **Example** 

```
Calculate lResult as strspn(lString1,lString2)
```

```
# lResult is a 1-based index, or len(lString1)+1 if all characters are in lString2
```

## **strtok()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_String_|NO|All|



## **Syntax** 

**strtok** (‘string1’,string2) 

## **Description** 

Tokenises _string1_ , using _string2_ as the delimiter with which to tokenize. 

This function returns tokens which are a substring of _string1_ until any character in _string2_ matches a character in _string1_ . When **strtok()** is called, the token found in _string1_ is removed, so that the function looks for the next token the next time it is called. 

**Note: strtok()** does not support null characters in _string1_ or _string2._ 

## **Example** 

```
Calculate lString1 as "The quick brown fox, jumped over the lazy dog"
Repeat Calculate lString2 as strtok('lString1'," ")
```

```
OK message {Token = [lString2]}
Until lString2=''
```

```
# returns each word in lString1 in an OK Message
```

## **stsetcol()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Client String Table_|NO|All|



## **Syntax** 

**stsetcol** ( _table,col_ ) 

139 



## **Description** 

Sets the current column for lookups from string table _table_ to the column with name _col_ and returns Boolean true for success (iOS plug-in client methods only). 

## **style()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_String_|YES|All|



## **Syntax** 

**style** (textescape[,value]) 

## **Description** 

Returns a style sequence suitable for embedding in styled text. _textEscape_ is a kEsc… constant; _value_ is a suitable value for the particular _textEscape._ 

Valid constants for the _style-character_ are listed under ‘Text escapes’ in the Constants pane of the IDE Catalog window (there is also a group called ‘JavaScript text escapes’ for the JavaScript client). Depending on the style character, you may also need to specify a _value_ , which itself can be a constant. You can use this function to format the columns in a headed list box field; in this case, you can insert an icon by specifying its ID, change the text color, or set a text style such as italic. 

Note that the alignment escapes (kEscCTab, kEscLTab and kEscRTab) are not designed to work with the headed list box. The headed list box method $setcolumnalign() can be used to set the alignment of a column. 

The JavaScript client supports a subset of the standard text escapes, and some additional values specific to the JavaScript client, as follows: 

|Constant|Description|
|---|---|
|**kEscColor**|In a client-executed method, the color parameter|
||must be a numeric literal or constant.|
|**kEscStyle**|In a client-executed method, the style parameter|
||must be a numeric literal or constant.|
|**kEscBmp**|In a client-executed method, the icon id|
||parameter must be either a numeric literal, or the|
||sum of a numeric literal and an icon size constant|
||e.g. 1710+k48x48|
|**kEscJsNewline**|No additional parameters are required. Inserts a|
||<br> line break tag. There is also a new function|
||br() which can be used as short-hand to do this.|
|**kEscJsClose**|No additional parameters are required. Closes the|
||current open style information (inserted by|
||kEscColor or kEscStyle) in the styled text and|
||reverts to the original color and text style. Note|
||-kEscColor and kEscStyle insert a <span> tag to|
||style the text. kEscJsClose closes the <span> tag.|
|**kEscJsHtml**|Inserts raw HTML (the second parameter to|
||style()).|



## **Example** 

```
# to format the columns in a headed list box you could use the following calculation
Do con(lCol1,style(kEscBmp,1756),kTab,lCol2,style(kEscColor,kRed),kTab,lCol3,style(kEscStyle,kItalic))
# give lCol1 a blue spot icon, lCol2 is red and lCol3 italic
```

140 



**styledtohtml()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_String_|YES|All|



## **Syntax** 

**styledtohtml** ( _styledtext_ ) 

## **Description** 

Converts _styledtext_ (a character string with styles embedded using the _style_ () function) into HTML (JavaScript client only, execute on client only; this function cannot be used in a server method). 

## **sys()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|NO|All|



## **Syntax** 

**sys** (number) 

## **Description** 

Returns information about the current system depending on a _number_ argument. 

Using the **sys()** function, you can obtain system information such as the current printer name, the pathname of the current library, the screen width or height in pixels, and so on. 

You can use the following _number_ values with the sys() function. 

|Number|Description|
|---|---|
|1|returns the Omnis version number.|
|2|returns the Omnis program type byte:bit 0 = full program (value 1),bit 1 = runtime|
||(value 2), bit 2 = evaluation (value 4),bit 4 = Unicode (value 16) - always set.Note|
||that the current version of Omnis does not support the use of “integrated”|
||versions.|
|3|returns your company name entered on installation.|
|4|returns your name entered on installation.|
|5|returns your serial number entered on installation.|
|6|returns the platform code of the current executable:‘N’ = Windows NT, 2000,|
||2003, XP, Vista, Windows 7/8/10.‘U’ = Linux.‘X’ = macOS.(‘W’ = Windows 95, 98 or|
||ME is no longer used)|
|7|returns a string containing the version number of the current OS. For example,|
||returns “6.2” under Windows 10, and “10.4.8” under macOS 10.4.8|
|8|returns the platform type of the current Omnis program as a string: ‘MAC64’,|
||‘MACARM’ (Apple M1), ‘WIN32’, ‘WIN64’, ‘UNIX’|
|9|returns the pathname separator for the current platform: ‘\’ (back slash) for|
||Windows,‘/’ (forward slash) for Unix and 64-bit macOS (32-bit Macs will return :)|
|10|returns the pathname of the current open library fle.|
|11,..,20|returns the pathname(s) of the current open data fle segment(s) (empty if none|
||are open).|
|21|returns the pathname of the current print fle name (empty if not open).|
|22|returns the pathname of the current import fle name (empty if not open).|
|23|returns the current port name (empty if no port open).|



141 



|Number|Description|
|---|---|
|24|returns the current report device, for example, Printer, Screen, Preview, File|
||(Preview is the default).|
|30,..,49|returns the name of the installed user-defned fat client menu(s) starting from|
||the left-most menu (empty if none are installed).|
|50,..,79|returns the name of the open user-defned fat client window(s) starting with the|
||top window (empty if none are open).|
|80|returns the current report name (empty if no report set).|
|81|returns the current search name (empty if no search set).|
|82|returns the main fle name (empty if no main fle set).|
|83|returns the number of records in main fle.|
|85|returns the name of currently executing method in the form class name/method|
||number.|
|86|returns a list of event parameters for the current event. The frst parameter is|
||always pEventCode containing an event code representing the event, for|
||example, evClick for a click on a button: a second or third event parameter may|
||be supplied which tells you more about the event|
|87|returns horizontal screen resolution in pixels per inch|
|88|returns vertical screen resolution in pixels per inch|
|89|returns the text for the current search calculation, or empty if no calculation is|
||set.|
|90|returns the number of methods on the method stack. This does not work for|
||client requests running in a thread of the Multi-threaded Server.|
|91|returns the decimal separator|
|92|returns the thousand separator|
|93|returns the parameter separator for calculations|
|94|returns the fle class feld name separator|
|101|returns the current printer name, and network path (empty if not connected).|
|104|returns the screen width in pixels.|
|105|returns the screen height in pixels.|
|106|macOS: not relevant - returns a fxed large value.Other platforms: returns the size|
||in bytes of available physical memory.|
|107|macOS: not relevant - returns a fxed large value.Other platforms: returns the|
||total size in bytes of physical memory.|
|108|macOS: not relevant - returns a fxed large value.Other platforms: returns a|
||number between 0 and 100 that gives a general idea of current memory|
||utilization, in which 0 indicates no memory use and 100 indicates full memory|
||use.|
|109|macOS: not relevant - returns zero.On Windows and Unix returns the unused|
||memory in bytes. This is the number of bytes available in the paging fle, added|
||to the number of bytes of available physical memory.|
|110|Deprecated. Does not return a value using the 64-bit versions of Omnis, and can|
||no longer be relied on as an accurate indicator of the processor type or computer|
||in use.Returns the CPU type.For Intel Processors:3 = 803864 = 804865 =|
||PentiumFor PowerMac Processors:257 = PowerPC 601259 = PowerPC 603260 =|
||PowerPC 604262 = PowerPC 603e263 = PowerPC 603ev264 = PowerPC 750 &|
||G3265 = PowerPC 604e266 = PowerPC 604ev268 = G4313 = G5|
|111|Deprecated. (macOS only) returns the Apple ROM version: 121 = SI, 124 = IIsi, CI &|
||FX.|
|114|Deprecated. (macOS only) returns 1 (true) if Apple events are available, 0|
||otherwise.|
|115|Returns the pathname of the folder containing the installed writeable fles,|
||including the terminating path separator. To get the pathname of the folder|
||containing the Omnis executable, use sys(215).|
|116|(Unix only) returns 1 (true) if Omnis has been confgured to force all fle names to|
||be lower case, 0 otherwise.|



142 



|Number|Description|
|---|---|
|118|(Windows only) returns additional information about the operating system|
||version. The information includes major and minor version numbers, a build|
||number, a platform identifer, and information about product suites and the|
||latest Service Pack installed on the system. This function returns the operating|
||system version information in the Windows OSVERSIONINFOEX structure, so|
||you should obtain information about this structure for full details about the|
||information returned (see the Microsoft web site).|
|120|(Windows only) returns the width of the current dialog base-width unit based on|
||the current system font; this differs for Small and Large font mode.|
|121|(Windows only) returns the height of the current dialog base-width unit based|
||on the current system font; this differs for Small and Large font mode.|
|122|returns true if the Web Client server communications listener started|
||successfully. It returns false if listener startup failed, or has not yet occurred.|
|123|returns the build number of the Omnis executable. The Omnis About box shows|
||the same build number in the version string|
|130-138|Not supported in Omnis Studio 5.0 and later.|
|185|returns the current executing method in the|
||format:Libraryname.Classname/Methodname/LinenumberThis is in addition to|
||sys(85) which returns the current executing method in the form|
||Classname/Methodname.|
|190|returns the number of times Omnis has loaded a class from disk and added it to|
||the memory class cache.|
|191|returns the number of times Omnis deleted a memory class cache entry, when it|
||added a class to the cache, meaning that the class deleted from the cache may|
||need to be reloadedsys(190) and sys(191) provide information you can use to|
||monitor the impact of changing the preference_root._prefs.$maxcachedclasses.|
||Too low a value for this preference may result in a performance hit, due to too|
||many classes being repeatedly loaded from disk.|
|192|sys(192) caters for both error handlers and other situations where information|
||about the method stack might be useful. It returns a list representing the|
||current method call stack (with a line for each line that would appear on the|
||debugger stack menu). The frst line in the list corresponds to the call to sys(192),|
||and subsequent lines corresponding to how the method running the previous|
||line was called.The list has the following columns:classitem - item reference to|
||the class containing the method.object - the name of the object containing the|
||method in the class; empty if it is a class method.method - the name of the|
||executing method.line - the line number of the executing method line.linetext -|
||the text for the executing method line.params - the parameters passed to the|
||method. This is a two-column list, with columns name and value. The value is|
||the value that would be displayed as a variable tooltip for the|
||parameter.methoditem - item reference to the method.inst - item reference to|
||the instance executing the method.The “sys192excludesIDEmethods” item in the|
||“defaults” section of confg.json, specifes whether or not to include IDE method|
||calls in the list returned from sys(192) (the default is true). This will exclude an IDE|
||method if the library containing the method is marked as always private.The|
||“sys192ListRowLimit”: N item (with N added) in the “defaults” section of|
||confg.json allows lists (and rows) with up to N rows to be included as a third|
||column in the output parameter data. If N <= 0 (the default) then no third|
||column is added. If N > 0, then each parameter in the parameter list stored in|
||each line of the sys(192/292) list has a third column, which for lists and rows|
||contains the actual list (or row) data, if the list or row has less than or equal to N|
||lines. In all other cases (not a list or row, or line limit N exceeded) column 3 is|
||empty.|
|193|returns a list which is a copy of the trace log.|



143 



|Number|Description|
|---|---|
|194|returns the list of open windows in the IDE. The list has the following|
||columns:windowname - the name of the window, as it would appear in the|
||windows menuclassitem - if the window is a class or method editor, the item|
||reference to the class; otherwise nullismethodeditor - boolean, true if and only if|
||the window is a method editor windowThe current line is non-zero if and only if|
||the window is the top design window, i.e. the top class editor or method editor|
||window. When deciding the top design window, the catalog, component store,|
||and property inspector are ignored.|
|195|returns the list of selected objects, if there is a top design window (as defned by|
||sys(194) above), and if the top design window is a window, report, toolbar, menu,|
||or remote form editor (NOT a method editor). The list has one|
||column:objectitem - the item reference of the selected object|
|196|returns the list of all open libraries (including private libraries) and their VCS build|
||properties. The list has the following columns: name - the internal name of the|
||librarypathname - the pathname of the library flevcsbuildersname - the|
||$vcsbuildersname property of the libraryvcsbuildnotes - the $vcsbuildnotes|
||property of the libraryvcsbuilddate - the $vcsbuilddate property of the library|
|197|Deprecated. Returns true (1) if running on Windows XP with themes enabled,|
||false (0) if not.|
|198|Returns the Bind status: an integer which indicates the status of binding the|
||web client server port number to the socket on which the server receives|
||incoming connections. The value is -1 if bind has not been attempted yet, 0 if|
||bind was successful, or a positive value (a socket layer error code) if the bind|
||failed|
|199|returns a list with a row for each method command. The list has two columns:|
||column 1 is the command group, column 2 is the command name|
|202|returns the command line parameters passed to Omnis.If the frst argument|
||passed via the command line is not a library, you can prepend it with a - (hyphen)|
||character. So when using sys(202), you will get all arguments passed to Omnis,|
||including the frst argument, whether it starts with a hyphen or not|
|203|(Win32/Win64 only) returns 1 (true) if Omnis is running as a service|
|204|returns a list with a row for each function. The list has three columns: column 1 is|
||the function group, column 2 is the function name and column 3 is the function|
||description|
|205|returns the byte ordering of the hardware. True (1) for big-endian machines, false|
||(0) for little-endian machines.|
|209|for macOS, returns the pathname of the folder containing the Omnis.app|
||bundle, including the terminating path separator; this may be different to the|
||pathname of the folder containing the Omnis executable (returned by sys(115)) if|
||you are using Omnis as a bundle. For other platforms, returns the same|
||pathname as sys(115).|
|210|returns the number of processors for the current machine (depending on the|
||information reported by the operating system, the value may not refect logical|
||processor cores).|
|212|returns the list of sort felds for the executing method stack. The list has the|
||following columns:name - the name of the sort felddescending - boolean, true if|
||this feld is sorted in descending orderupper - boolean, true if sorting of this feld|
||is case-insensitivesubtotals - boolean, true if subtotals are printed when the sort|
||feld changesnewpage - boolean, true if a new page is started when the sort feld|
||changes|
|215|Returns the pathname of the folder containing the Omnis executable, including|
||the terminating path separator.|
|216|Returns the pathname of the currently executing Omnis program.|
|218|Modifes the OEM character conversion table to leave CR and LF unchanged.|
|219|Restores the OEM character conversion table to the original mappings for CR|
||and LF.|
|228|Modifes the OEM character conversion table to leave TAB unchanged.|
|229|Restores the OEM character conversion table to the original mapping for TAB.|



144 



|Number|Description|
|---|---|
|232|(Win32/Win64 only) returns 1 (true) if Omnis is running as an elevated user or|
||administrator|
|233|(Windows and Linux only) Returns the title of the main Omnis window|
|234|Returns a row containing statistics about RESTful requests to the Omnis Server.|
||The row has three columns: column 1 is the count of successful calls, column 2 is|
||the count of calls resulting in an error, column 3 is the count of calls internally|
||requeued because there was not a free user|
|235|Returns the value of the server confguration item timeOffsetMinutes in|
||confg.json. Omnis adds this to the current system date-time when generating|
||the value for #D and #T. timeOffsetMinutes defaults to zero if it is not present in|
||confg.json|
|236|Returns true if VCS branching is enabled.|
|237|Returns an item reference to the method currently being edited, if the method|
||editor is the top window (and only one method is selected).|
|238|Returns 1 (true) if the remote debug server is running|
|239|Returns true if the Startup method in the library has fnished, or false if not|
|240|Returns a string that identifes the current monitor confguration. You could use|
||this in your code to branch according to the monitor confguration of end users|
|241|Returns a list containing the fnd and replace log list from $fndandreplace.|
||Where possible, the 6th column named ‘item’ contains an item reference either|
||directly to the found data, such as a method line, or to the item containing the|
||found data, such as a property|
|242|Returns a string which uniquely identifes the current child process when|
||running in the Multi Process Server. If the current process is not a child process,|
||returns 0.|
|243|Returns true if Omnis is currently running as a Multi Process Server.|
|250|Returns a list of fles which were used to open Omnis, e.g. double-clicked from|
||the Finder, or passed on the command line. This is empty if Omnis was opened|
||directly by double-clicking|
|251|On Windows, returns the_width_of the available area of the main application|
||window; the same information is returned in the $mainresized task message.|
||On macOS, returns the overall_width_of all screens|
|252|On Windows, returns the_height_of the available area of the main application|
||window; the same information is returned in the $mainresized task message.On|
||macOS, return the overall_height_of all screens|
|253|Returns true if Omnis is using dark mode.|
|254|Returns the pathname of the folder where Omnis writes scripts and other fles|
||used to generate PDF documents.|
|255|Returns the pathname of the folder where Omnis writes temporary PDF fles.|
|256|Returns the maximum server license count.|
|257|Returns the current number of server licenses in use.|
|290|Returns the number of methods on the method stack excluding any that are to|
||be cleared. This does not work for client requests running in a thread of the|
||Multi-threaded Server.|
|292|Returns an empty or single line list containing the same columns as sys(192)|
||where the line represents the calling method; see sys(192)|
|3000|Turn on logging of method command execution.|
|3001|Turn off logging of method command execution.|
|3003|Include method commands executed by IDE tasks in method command|
||logging turned on using sys(3000).|
|3004|Exclude method commands executed by IDE tasks from method command|
||logging turned on using sys(3000).|



## **Example** 

The following example uses _sys(6)_ to test the current OS and branches accordingly. 

```
Calculate lPlatform as sys(6)
```

145 



```
If lPlatform='X' ## on macOS
```

```
Do FileOps.$createdir('/Omnis/Test')
```

```
Else If lPlatform='U' ## on Linux
```

```
Do FileOps.$createdir('/home/omnis/test')
```

```
Else ## on Windows platforms
```

```
Do FileOps.$createdir('c:\Omnis\test')
End If
```

## **systemversion()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|NO|All|



## **Syntax** 

**systemversion** () 

## **Description** 

Returns a row of version information about the current operating system, with columns platform, major, minor, build, and server. The platform parameter is the platform code; major, minor, and build identify the system version (not for Linux); server is true for Window server systems. 

Note this function replaces all the “is…()” functions (e.g. iswindows10()) for determining the current operating system version. 

## **tan()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Trigonometric_|YES|All|



## **Syntax** 

**tan** (number) 

## **Description** 

Returns the Tangent of an _angle_ where the _angle_ is in degrees (or radians if #RAD is true). 

## **Example** 

```
Calculate lResult as tan(45)
# returns 1
```

## **textsize()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Font handling_|NO|Windows,Linux|



## **Syntax** 

**textsize** (string,fontname,pointsize,style,‘width’,‘depth’) 

146 



## **Description** 

Returns the width and depth in pixels of the specified text or string. 

instead. 

The _string_ parameter can be a literal string or character variable with a maximum length of 255; _fontname_ is the name of the font; _pointsize_ the point size of the font; _style_ is represented by an integer, that is, 0 = Normal, 1 = Bold, 2 = Italic, 4 = Underline (or a combination of these: 3 would be bold-italic, for example). The _width_ and _depth_ parameters hold the returned values in pixels. The _width_ and _depth_ parameters are integer variables to hold the width and depth values returned; these must be in quotes. The function also returns a value of 0 to indicate the font does not exist or an error occurred, otherwise 1 is returned indicating the text was found. 

## **Example** 

```
Calculate lFontStyle as 6 ;; Italic Underline
Calculate lFontName as "Arial"
Calculate lFontSize as 16
If textsize(lString,lFontName,lFontSize,lFontStyle,'lWidth','lDepth')<>0
```

```
# do something depending on lWidth and lDepth
Else
```

```
# font didn't exist or error occurred
End If
```

## **tim()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Date and Time_|NO|All|



## **Syntax** 

**tim** (number[,timeformat]) 

## **Description** 

Converts the specified _number_ value to a time determined by the _timeformat_ argument and returns the result; #FT is used as the time formatting string if the second argument is not specified. 

If the first argument is already a date/time, its format is changed to the format given by the second argument. 

The #FT string defaults to ‘H:N’ and so _tim_ ( _number_ ) takes _number_ to be a number of minutes. If you supply a format string such as ‘N.S’, _number_ will be taken as a number of seconds. 

With a second argument, **tim()** is equivalent to dat() with two arguments. The format string determines how the conversion is carried out. 

## **Example** 

```
Calculate lTime as tim(1)
# returns 00:01 when #FT is H:N (the default)
```

```
Calculate lTime as tim(950)
# returns 15:50
```

```
Calculate lTime as tim(950,'H:N.S')
# returns 00:15.50, that is 950 seconds
```

147 



**tot()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_List_|NO|All|



## **Syntax** 

**tot** ([listname,]fieldname) 

## **Description** 

Returns the total of the stored values of _fieldname_ in a list specified by _listname_ . 

The _fieldname_ argument must be a field stored in the list, not a constant or expression. If the _listname_ argument is not specified the current list is used. This function does not work for table based lists. If _fieldname_ is not a numeric field, all values are converted to their numeric equivalents before being accumulated. 

## **Example** 

```
Calculate lResult as tot(lList,lCol1)
```

```
# returns total of all lCol1 field values stored in the list lList
```

```
Calculate lResult as tot(lCol1)
```

```
# returns total of all lCol1 field values stored in current list
```

```
Calculate lResult as tot(#LSEL)
```

```
# returns total number of selected lines in the current list
```

## **totc()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_List_|NO|All|



## **Syntax** 

**totc** ([listname,]expression) 

## **Description** 

Returns the total of an _expression_ evaluated for a list specified by _listname_ . 

If the _listname_ argument is not specified, the current list is used. This function does not work for table based lists. The _expression_ is totaled for the lines in the specified list. 

This is a more general version of the _tot()_ function. 

## **Example** 

```
# If list lList contains field lCol1, the sum of the
```

- `# squares of all values of lCol1 in the list is:` 

- `# note that totc(lList,lCol1) is the same as tot(lList1,lCol1) Calculate lResult as totc(lList,lCol1*lCol1)` 

148 



**tracelog()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|YES|All|



## **Syntax** 

**tracelog** ( _string_ ) 

## **Description** 

Writes the string to the trace log (or JavaScript console for client-executed code). Does nothing if debugging is disabled using the library property $nodebug. Returns the string if the string was written, or #NULL if it was not written. 

## **trim()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_String_|YES|All|



## **Syntax** 

**trim** (string[,leading=ktrue,trailing=ktrue,character=space_char]) 

## **Description** 

Removes the specified _leading_ and/or _trailing_ character from the _string_ . 

You specify the character to be removed in the _character_ argument. If this is omitted the space character is removed from the string by default. 

## **Example** 

```
Calculate lString as trim(' ABCDE')
```

```
# returns 'ABCDE'
```

```
Calculate lString as trim('*****ABCDE*****',kTrue,kFalse,'*')
```

```
# returns 'ABCDE*****'
```

## **truergb()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_General_|NO|All|



## **Syntax** 

**truergb** ( _color_ ) 

## **Description** 

Converts the specified _color_ into its true RGB value and returns the result. 

149 



**Example** 

```
Calculate lValue as truergb(kRed)
# returns RGB value for red
```

```
Calculate lValue as truergb(rgb(255,0,0))
```

```
# returns RGB value for red
```

## **tzcurrent()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Date and Time_|NO|All|



## **Syntax** 

**tzcurrent** () 

## **Description** 

Returns the character string identifying the time zone of the current date and time. The result can be mapped to an alternative using the Built-in strings. 

## **tzdaylight()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Date and Time_|NO|All|



## **Syntax** 

**tzdaylight** () 

## **Description** 

Returns the character string identifying the daylight saving time zone. The result can be mapped to an alternative using the built-in strings. 

## **tzoffset()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Date and Time_|NO|All|



## **Syntax** 

**tzoffset** () 

## **Description** 

Returns the system time zone offset from UTC time in minutes. 

## **tzstandard()** 

150 



Function group Execute on client Platform(s) _Date and Time_ NO All 

## **Syntax** 

**tzstandard** () 

## **Description** 

Returns the character string identifying the standard time zone. The result can be mapped to an alternative using the built-in strings. 

## **uncompress()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Compression_|NO|All|



## **Syntax** 

**uncompress** (binary,uncompressed-length) 

## **Description** 

Uncompresses the _binary_ variable (containing the result of the previous call to _compress_ ()) and returns the binary uncompressed data. 

Note you need to supply the length of the original uncompressed data. 

## **Example** 

```
Calculate lOriginal as uncompress(lCompressed,50)
```

## **unichr()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Unicode_|YES|All|



## **Syntax** 

**unichr** (code1[,code2]…) 

## **Description** 

Returns a string formed by concatenating the supplied Unicode character codes. Each code is either a number or a string of the form ‘U+h’, where h is 1-6 characters representing a hexadecimal value. 

## **unicode()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Unicode_|YES|All|



151 



**Syntax** 

**unicode** (string,position[,hex]) 

## **Description** 

Returns the Unicode value of the character at the _position_ in the _string_ . The first _position_ in the _string_ is 1. If Boolean _hex_ is true (default false) it returns a hex string ‘U+h’. 

## **uniconv()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Unicode_|NO|All|



## **Syntax** 

**uniconv** (srctype,src,dsttype,dst,bom,errtxt) 

## **Description** 

Converts _src_ to _dst_ . Returns zero if ok, or errcode and _errtxt_ . _Types_ are kUniType… constants (not binary). If Boolean _Bom_ is true, _dst_ has a Unicode BOM if it can. 

You can handle CR, LF and TAB characters using the following sys() functions: 

|sys()|Description|
|---|---|
|218|Modifes the OEM character conversion table to leave CR and LF unchanged.|
|219|Restores the OEM character conversion table to the original mappings for CR and LF.|
|228|Modifes the OEM character conversion table to leave TAB unchanged.|
|229|Restores the OEM character conversion table to the original mapping for TAB.|



## **upp()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_String_|YES|All|



## **Syntax** 

**upp** (string) 

## **Description** 

Returns the upper case representation of a _string_ . Any non-alphabetic characters in the _string_ are ignored. 

## **Example** 

```
Calculate lString as upp('Author')
# returns 'AUTHOR'
Calculate lString as upp('oMnIs')
# returns 'OMNIS'
Calculate lString as upp(mid('peripheral',3,3))
# returns 'RIP'
```

152 



**useradians()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Trigonometric_|YES|All|



## **Syntax** 

**useradians** ( _[useradians]_ ) 

## **Description** 

Sets or returns #RAD. Either sets #RAD and returns the previous value, or if no parameter is supplied returns the current value of #RAD. 

## **utctoloc()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Date and Time_|NO|All|



## **Syntax** 

**utctoloc** ( _datetime_ ) 

## **Description** 

Converts the _datetime_ (or time) from UTC (Coordinated Universal Time) to the local timezone, and returns the result. 

## **utf8tochar()** 

|Function group|Execute on client|Platform(s)|
|---|---|---|
|_Unicode_|NO|All|



## **Syntax** 

**utf8tochar** ( _utf8_ ) 

## **Description** 

Returns the character string which is represented by the UTF-8 encoded parameter. 

## **Binary Field** 

## **Functions** 

_bdif() binchecksum()bincompare()_ binfrombase32() _binfrombase64()binfromhex() binfromint32()binfromint64() binlength() binsearch()_ bintobase32() _bintobase64() bintohex() bintoint32() bintoint64() bitand()_ 

153 



_bitclear() bitfirst() bitmid() bitnot() bitor() bitrotatel() bitrotater() bitset() bitshiftl() bitshiftr() bittest() bitxor() bundif() bytecon() byteget() bytemid() byteset() decxtea() encxtea()_ sha256() sha512() 

**Class Functions Client String Table Functions Compression Functions** 

_cdif() cundif() stgetcol() stsetcol() compress() uncompress()_ 

**Date and Time Functions** 

|_dadd()_|_dat()_|_ddiff()_|_dim()_|
|---|---|---|---|
|_dname()_|_dpart()_|_dtcy()_|_dtd()_|
|_dtm()_|_dtw()_|_dty()_|_fday()_|
|_fmtdatetime()_<br>_fmtshortdate()fmtshorttime()_<br>_getdatetime()_||||
|_getfye()_|_getticks()_|_getws()_|iso8601toomnis()|
|_isoweek()_|isoweekstart()|_lday()_|_loctoutc()_|
|_nday()_|omnistoiso8601()<br>_pday()_||_setfye()_|
|_setws()_|_tim()_|_tzcurrent()_|_tzdaylight()_|
|tzoffset()|_tzstandard()_|_utctoloc()_||



**DNet Functions** 

154 



_DNet.$addclass()DNet.$basefolder()DNet.$getenum()_ 

## **External Functions** 

_Strip()_ **Field Functions** _fld() nam()_ **FileOps Static Functions** _FileOps.$changeworkingdir()FileOps.$converthfsFileO_ _**p** athtoposixpath()s.$convertposixpathtohfspath()FileOps.$copyfile() FileOps.$creatFil_ _**e** dir()Ops.$deletefiFi_ _**le** Ops.$doesfileexist()() FileOps.$filelist() FileOps.$getfiFi_ _**le** info()Ops.$getfilename()FileOps.$getlasterror()FileOps.$getunixpermissions() FileOps.$getworkingdir()FileOps.$movefF leOps.$parentdir()le() FileOps.$putfilename()_ FileOps.$readfile() _FileOps.$rename()FileOps.$selectdirectory()FileOps.$selectfilesinsystemviewer() FileOps.$setfF leOps.$setunixpermissions()leinfo() FileOps.$splitpathname()FileOps.$writefile()_ 

Note: FileOps.$writeentirefile() and FileOps.$readentirefile() are obsolete and have been removed from the Catalog; use their equivalent functions FileOps.$writefile() and FileOps.$readfile() as above, or the dynamic functions below. 

## **FileOps External Object** 

## **Dynamic Functions (Methods)** 

The FileOps dynamic functions allow you to manipulate files. To use these methods, you must declare an object variable, and set its subtype to the FileOps external object. You then call the method using the syntax object.$methodname(). You can use the Interface Manager to view the methods of the object. 

The FileOps external object has the following methods. 

$closefile() $createfile() $createtmpfile()$getfileinfo() $getlasterror()$getposition() $isopen() $openfile() $readcharacter()$readfile() $setfileinfo()$setfilesize() $writecharacter()$writefile() 

## **FileOps Worker Objects** 

The FileOps Worker Objects, **FileOpsCopyWorker, FileOpsMoveWorker,** and **FileOpsDeleteWorker** allow you to copy, move or delete files asynchronously, which may be useful when operating on a large number of files. 

155 



To use the FileOps workers, you need to create an Object variable and set its subtype to one of the FileOps worker objects via the Select Object dialog. Alternatively, you can create an Object class and set its superclass to one of the FileOps worker objects, then create an Object variable or Object reference variable and set its subtype to the object class name. Having created the variable you can call its methods using OBJECTVAR.$methodname. 

The FileOps workers work exactly like the other workers, including the ability to run the $init, $start or $run methods. They have the property $progressinterval which sets an interval in seconds, at which progress notifications are sent to the $progress method. $progressinterval defaults to the minimum value of 1 second. 

For the $init method, the parameters are the same as used in the static methods of the FileOps object to copyfile, movefile or deletefile. 

When $completed is called, a row is returned with the errorCode and errorText of the action; errorCode will be 0 if there is no error, otherwise a FileOps Worker error is returned, plus the error description in the errorText column. 

When the $progress method is called (only if $callprogress is true), a row is returned with a column name ‘progress’ containing an estimated number between 0 and 100 indicating the percentage progress of the file operation. Note: the Delete worker never calls $progress, therefore progress notifications are not sent from the delete worker. 

Note that if you try to cancel a FileOps worker while it is running, the main thread will be blocked until the worker finishes its job. 

**==> picture [60 x 197] intentionally omitted <==**

**----- Start of picture text -----**<br>
Financial<br>Functions<br>Font Handling<br>Functions<br>FontOps<br>Functions<br>**----- End of picture text -----**<br>


**==> picture [42 x 25] intentionally omitted <==**

**----- Start of picture text -----**<br>
General<br>Functions<br>**----- End of picture text -----**<br>


_ann() anna() cmp() fontlist() isfontinstalled()textsize() FontOps.$replistfonts()FontOps.$reptextheight()FontOps.$reptextwidth()FontOps.$winlistfonts() FontOps.$wintextheight()FontOps.$wintextwidth() alt() basecolor() callprivate()cmd()_ complementarycolor() _ctrl() errcode() errtext() eval() evalf() flag() format() getenv()_ hexcolor() hsla() iconidwithbadge() _iconurl() isclear()_ isclient() _isheadless() isleopard() islion() ismountainl_ _**i** on()snull() issnowleopard()isvista() iswindows10()iswindows11()_ 

156 



_iswindows7()iswindows8() iswindows81()iswindowsserver()_ 

_listenv() msgcancelled()not() pathsep() platform() printf() putenv() rgb()_ rgba() _shift() sleep() sys()_ systemversion() _tracelog() truergb()_ 

## **JavaObjs Library** 

## **Functions** 

Support for the JavaObjs Library functions $addclass() and $resetclasscache() has been removed in Studio 10, but the library is available from support if required. 

_JavaObjs JavaObjs LiLibrary.$addclass()brary.$resetclasscache()_ 

## **List** 

**Functions** 

**Logarithmic** 

**Functions** 

**Lookup** 

**Functions** 

_avgc() cnubintolist() list() lst() maxc() minc() row() stddevc() tot() totc() exp() ln() log() lookup() max() min() pick()_ 

**Mouse** 

## **Functions** 

_These functions are for desktop apps using Window classes only, not web or mobile apps._ 

_mousedn() mouseover() mouseup() rmousedn() rmouseup()_ 

157 

