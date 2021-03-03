import csv

inputName = "output.csv"

raw_f = open(inputName, 'rt', encoding='UTF-8')
rdr = csv.reader(raw_f, delimiter=",")
linecnt = 1
filecnt = 0
output_f = open("PHASE4_dataset"+"_"+str(filecnt)+".csv", 'w', encoding='UTF-8')
wtr = csv.writer(output_f, lineterminator='\n')
for line in rdr:
    if linecnt % 50000 == 0:
        output_f.close()
        print("PHASE4_dataset"+"_"+str(filecnt)+".csv is created.")
        filecnt = filecnt + 1
        output_f = open("PHASE4_dataset"+"_"+str(filecnt)+".csv", 'w', encoding='UTF-8')
        wtr = csv.writer(output_f, lineterminator='\n')
        wtr.writerow(["ID", "DATE", "SENTENCE", "SUBJ", "PRED", "OBJ"])
    wtr.writerow(line)
    linecnt = linecnt + 1
output_f.close()
print("PHASE4_dataset"+"_"+str(filecnt)+".csv is created.")
print("Finished..")
