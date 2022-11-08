import pyembroidery as pe

outfile="firstgo"

stitches=[];
stitches2=[];
for i in range(-20,21):
    stitches.append([i,i*i])
    stitches2.append([2*i,i*i])


p1= pe.EmbPattern()
p1.add_block(stitches, "blue")
p1.add_block(stitches2, "red")

pe.write_dst(p1, f"{outfile}.dst")
pe.write_png(p1, f"{outfile}.png")
