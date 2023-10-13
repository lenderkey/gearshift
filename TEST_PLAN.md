# test plan

## read / write

Test reading and writing to a file. This shouild include all modes, 
including ones that will fail. 

```python
with gearshift.open("file.txt", "w") as fout:
    fout.write(data)

with gearshift.open("file.txt", "r") as fin:
    print(fin.read())
```

## vault / local

Gearshift can be run with vault or without. Normally
we will test all the other functionalities without.

## extended files

We should test adding blocks to AES0 files that are not
on our standard list. Some should fail (A-Z), others
should not

## CLI

encrypt / decrypt - may need some work to bring into line with IO