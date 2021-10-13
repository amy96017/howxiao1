from os import close
import re
import py_midicsv as pm

#input file name
filename = input()
csv_string = pm.midi_to_csv(filename)
filename = filename.strip(".mid")

# Load the MIDI file and parse it into CSV format
with open("%s_converted.csv"%(filename), "w") as f:
    f.writelines(csv_string)
'''
# Parse the CSV output of the previous command back into a MIDI file
midi_object = pm.csv_to_midi(csv_string)

# Save the parsed MIDI file to disk
with open("%s_converted.mid"%(filename), "wb") as output_file:
    midi_writer = pm.FileWriter(output_file)
    midi_writer.write(midi_object)
'''

#.csv to prepocess file
with open("%s_converted.csv"%(filename),'r') as f:
    notes_duration = []
    notes_pitch = []
    lyrics = []
    division = 1 
    note_on = -1
    note_off = -1
    pitch = '0'
    lyric_check = False
    for line in f:
        per_line = line.split(', ')#看到','就分隔一次

        #the first line, get division(quarter note lenghth)
        if(per_line[2]=='Header'):
                division = int(per_line[5])

        #get lyrics
        elif(per_line[2]=='Lyric_t'):
            lyric = re.sub(r'\s+','',per_line[3]) #remove \n(換行),(如有字符間有多個空格直接把"\s" 寫成 "\s+" 讓空格重複
            #re.sub第一個參數的r是什麼意思??
            #把所有空白字符換成空白鍵
            lyric = lyric.strip("\"")#刪除頭尾的'"'
            lyrics.append(lyric)
            lyric = True#將這格的lyric清除成default

        #get note on
        elif(per_line[2]=='Note_on_c'):
            #check if this note has lyric
            '''
            if lyric_check == False:
                print("Error! Some notes don't have its own lyric.")
                 exit()
            '''
            if(per_line[5]=='0\n'):
                note_off = int(per_line[1])
                duration = round((note_off - note_on)/division, 2)
                pitch = per_line[4]
                notes_duration.append(duration)
                notes_pitch.append(pitch)
                note_on = -1
                lyric_check = False
            

        #get note off
        elif(per_line[2]=='Note_off_c'):
            note_off = int(per_line[1])
            duration = round((note_off - note_on)/division, 2)
            pitch = per_line[4]
            notes_duration.append(duration)
            notes_pitch.append(pitch)
            note_on = -1
            lyric_check = False

        
        if(note_on == -1): #if there are note_on before, than there is polyphony
            note_on = int(per_line[1])

            #silence between notes, output sil
            if(note_on != note_off and note_off != -1): #silence between notes, output sil
                duration = round((note_on - note_off)/division, 2)
                pitch = '1'
                notes_duration.append(duration)
                notes_pitch.append(pitch)
                lyrics.append('sil')

        else:
            print("Error! Some notes are overlapping.")
            exit()                       


    #output text
    with open('text.txt','w') as output:
        while(1):
            #output lyrics
            #output.write('|')
            for i in range(10):
                if(not(lyrics)): break
                if(lyrics[0]=='sil'):
                    if(i==0): 
                        output.write("%s "%(lyrics.pop(0)))
                    elif(i==9 or len(lyrics)==1):
                        output.write(" %s"%(lyrics.pop(0)))
                    else:
                        output.write(" %s "%(lyrics.pop(0)))
                else:
                    output.write(lyrics.pop(0))

            #output notes pitch
            output.write('|')
            for i in range(10): #10 notes per line
                if(not(notes_pitch)): break
                if(i!=0): output.write(' ')
                output.write(notes_pitch.pop(0))

            #output notes duration
            output.write('|')
            for i in range(10):#10 notes per line
                if(not(notes_duration)): break
                if(i!=0): output.write(' ')
                output.write(str(notes_duration.pop(0)))
            if(not(notes_pitch)): break

            output.write('\n')