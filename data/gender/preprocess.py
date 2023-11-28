with open("train_original.pos", 'r') as male:
    with open("train.pos", 'w') as output_pos:
      for line in male:
          words = line.split()
          if(len(words) < 35):
              output_pos.write(line)
with open("train_original.neg", 'r') as female:
    with open("train.neg", 'w') as output_neg:
      for line in female:
          words = line.split()
          if(len(words) < 35):
              output_neg.write(line)