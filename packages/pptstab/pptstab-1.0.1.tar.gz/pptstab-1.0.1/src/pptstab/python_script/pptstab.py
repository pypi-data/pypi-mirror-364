import argparse
import warnings
import subprocess
import os
import sys
import numpy as np
import pandas as pd
import math
import itertools
from collections import Counter
import pickle
import re
import glob
import time
import uuid
from time import sleep
from tqdm import tqdm
import zipfile
import pandas as pd
import torch
# !pip install tf2onnx onnxruntime
import joblib
#import tf2onnx
import onnxruntime
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler

nf_path = os.path.dirname(__file__)
warnings.filterwarnings("ignore")

def embedd_extract(file):
    from transformers import BertModel, BertTokenizer
    df1 = file
    tokenizer = BertTokenizer.from_pretrained("Rostlab/prot_bert", do_lower_case=False)
    model = BertModel.from_pretrained("Rostlab/prot_bert")
    model.eval()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    protein_sequences = df1['Seq'].tolist()
    protein_sequences_tokenized = [' '.join(seq) for seq in protein_sequences]
    max_seq_length = 2500
    protein_sequences_tokenized = [seq[:max_seq_length] for seq in protein_sequences_tokenized]
    batch_size = 128
    embeddings_list = []
    for i in tqdm(range(0, len(protein_sequences_tokenized), batch_size), desc="Processing batches"):
        batch_sequences = protein_sequences_tokenized[i:i + batch_size]
        batch_outputs = []
        for seq in batch_sequences:
            outputs = tokenizer(
                seq,
                add_special_tokens=True,
                padding=True,
                truncation=True,
                return_tensors="pt"
            )
            inputs = {key: value.to(device) for key, value in outputs.items()}
            batch_outputs.append(inputs)
        with torch.no_grad():
            model_outputs = [model(**inputs) for inputs in batch_outputs]
            embeddings = [output.last_hidden_state.mean(dim=1) for output in model_outputs]
            embeddings_list.extend(embeddings)
    embeddings_result = torch.cat(embeddings_list, dim=0)
    df1['embeddings_output'] = embeddings_result.tolist()
    df22 = pd.DataFrame(df1['embeddings_output'].tolist())
    df33 = pd.concat([df1['Seq'], df22], axis=1)
    return df33

def process_embedd(file, Flag):
    df11 = file
    df = df11[['Seq']]
    df2 = df11.drop(['Seq'], axis = 1)
    colNumber = df2.shape[1]
    headerRow=[]
    for i in range(colNumber):
        headerRow.append('emb_'+str(i))
    df2.columns=headerRow
    
    user_input = Flag
    if Flag not in [0, 1]:
        print("Invalid input. Please enter 1 or 0. For 1, 'cell' is selected; for 0, 'lysate' is selected.")
        sys.exit(1)
    if user_input == 1:
        df2['lysate'] = 1
        df2['cell'] = 0
    elif user_input == 0:
        df2['lysate'] = 0
        df2['cell'] = 1
    else:
        print("Invalid input. Please enter 1 or 0.")
    return df2

def readseq(file):
    with open(file) as f:
        records = f.read()
    records = records.split('>')[1:]
    seqid = []
    seq = []
    for fasta in records:
        array = fasta.split('\n')
        name, sequence = array[0].split()[0], re.sub('[^ACDEFGHIKLMNPQRSTVWY-]', '', ''.join(array[1:]).upper())
        seqid.append('>'+name)
        seq.append(sequence)
    if len(seqid) == 0:
        f=open(file,"r")
        data1 = f.readlines()
        for each in data1:
            seq.append(each.replace('\n',''))
        for i in range (1,len(seq)+1):
            seqid.append(">Seq_"+str(i))
    df1 = pd.DataFrame(seqid)
    df2 = pd.DataFrame(seq)
    return df1,df2

def lenchk(file1):
    cc = []
    df1 = file1
    df1.columns = ['seq']
    for i in range(len(df1)):
        if len(df1['seq'][i])>30:
            cc.append(df1['seq'][i])
        else:
            cc.append(df1['seq'][i])
    df2 = pd.DataFrame(cc)
    df2.columns = ['Seq']
    return df2
def mutants(file1,file2):
    std = list("ACDEFGHIKLMNPQRSTVWY")
    cc = []
    dd = []
    ee = []
    df2 = file2
    df2.columns = ['Name']
    df1 = file1
    df1.columns = ['Seq']
    for k in range(len(df1)):
        cc.append(df1['Seq'][k])
        dd.append('Original_'+'Seq'+str(k+1))
        ee.append(df2['Name'][k])
        for i in range(0,len(df1['Seq'][k])):
            for j in std:
                if df1['Seq'][k][i]!=j:
                    dd.append('Mutant_'+df1['Seq'][k][i]+str(i+1)+j+'_Seq'+str(k+1))
                    cc.append(df1['Seq'][k][:i] + j + df1['Seq'][k][i + 1:])
                    ee.append(df2['Name'][k])
    xx = pd.concat([pd.DataFrame(ee),pd.DataFrame(dd),pd.DataFrame(cc)],axis=1)
    xx.columns = ['Seq_ID','Mutant_ID','Seq']
    return xx

def seq_pattern(file1,file2,num):
    df1 = file1
    df1.columns = ['Seq']
    df2 = file2
    df2.columns = ['Name']
    cc = []
    dd = []
    ee = []
    for i in range(len(df1)):
        for j in range(len(df1['Seq'][i])):
            xx = df1['Seq'][i][j:j+num]
            if len(xx) == num:
                cc.append(df2['Name'][i])
                dd.append('Pattern_'+str(j+1)+'_Seq'+str(i+1))
                ee.append(xx)
    df3 = pd.concat([pd.DataFrame(cc),pd.DataFrame(dd),pd.DataFrame(ee)],axis=1)
    df3.columns= ['Seq_ID','Pattern_ID','Seq']
    return df3
def feature_ser_gen(file, Flag):
    data = list((file).iloc[:,0])
    GH = []
    for i, seq in enumerate(data):
        seq = seq.upper()
        num, length = Counter(seq), len(seq)
        num = dict(sorted(num.items()))
        C = list(num.keys())
        F = list(num.values())
        my_list = {aa: 0 for aa in 'ACDEFGHIKLMNPQRSTVWY'}
        for key, value in my_list.items():
            for j in range(len(C)):
                if key == C[j]:
                    my_list[key] = round(((F[j] / length) * math.log(F[j] / length, 2)), 3)
        GH.append(list(my_list.values()))

    df = pd.DataFrame(GH)
    df.columns = ['SER_A','SER_C','SER_D','SER_E','SER_F','SER_G','SER_H','SER_I','SER_K','SER_L','SER_M','SER_N','SER_P','SER_Q','SER_R','SER_S','SER_T','SER_V','SER_W','SER_Y']
    
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler()
    df2 = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)

    user_input = Flag
    if Flag not in [0, 1]:
        print("Invalid input. Please enter 1 or 0. For 1, 'cell' is selected; for 0, 'lysate' is selected.")
        sys.exit(1)
    if user_input == 1:
        df2['lysate'] = 1
        df2['cell'] = 0
    elif user_input == 0:
        df2['lysate'] = 0
        df2['cell'] = 1
    else:
        print("Invalid input. Please enter 1 or 0.")
    return df2

def feature_aac_gen(file, Flag):
    std = list("ACDEFGHIKLMNPQRSTVWY")  # Define the amino acid abbreviations
    df = file
    sequences = df.iloc[:, 0][0:]
    output = "AAC_A,AAC_C,AAC_D,AAC_E,AAC_F,AAC_G,AAC_H,AAC_I,AAC_K,AAC_L,AAC_M,AAC_N,AAC_P,AAC_Q,AAC_R,AAC_S,AAC_T,AAC_V,AAC_W,AAC_Y\n"  # Header for the output
    result_data = []  # To store results for further processing
    for sequence in sequences:
        sequence_length = len(sequence)
        composition_values = []  # Store composition values for each sequence
        for amino_acid in std:
            count = sequence.count(amino_acid)
            composition = (count / sequence_length) * 100
            composition_values.append("%.2f" % composition)  # Append the composition value for each amino acid to the list
        output += ",".join(composition_values) + "\n"  # Add the composition values for the sequence to the output string
        result_data.append(composition_values)  # Store results for further processing
    rows = [row.split(',') for row in output.split('\n')]
    df = pd.DataFrame(rows[1:-1], columns=rows[0])
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler()
    df2 = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)   
    user_input = Flag
    if Flag not in [0, 1]:
        print("Invalid input. Please enter 1 or 0. For 1, 'cell' is selected; for 0, 'lysate' is selected.")
        sys.exit(1)
    if user_input == 1:
        df2['cell'] = 1
        df2['lysate'] = 0
    elif user_input == 0:
        df2['cell'] = 0
        df2['lysate'] = 1
    else:
        print("Invalid input. Please enter 1 or 0.")
    return df2
def model_run(file1, model1, model2):
    unseen_data_normalized = file1
    class CustomANN(tf.keras.Model):
        def __init__(self):
            super(CustomANN, self).__init__()
            self.dense1 = tf.keras.layers.Dense(64, activation='relu')
            self.dense2 = tf.keras.layers.Dense(32, activation='relu')
            self.output_layer = tf.keras.layers.Dense(1)

        def call(self, inputs):
            x = self.dense1(inputs)
            x = self.dense2(x)
            return self.output_layer(x)
    onnx_model_path = model1
    session_ann = onnxruntime.InferenceSession(onnx_model_path)
    mlp_regressor = joblib.load(model2)
    input_name_ann = session_ann.get_inputs()[0].name
    inputs_ann = {input_name_ann: np.array(unseen_data_normalized).astype(np.float32)}
    output_name_ann = session_ann.get_outputs()[0].name
    predictions_ann = session_ann.run([output_name_ann], inputs_ann)[0]
    predictions_mlp = mlp_regressor.predict(np.array(unseen_data_normalized))
    predictions_combined = (predictions_ann.flatten() + predictions_mlp) / 2
    predictions_df = pd.DataFrame(predictions_combined, columns=['Predicted_Tm'])
    original_min = 30
    original_max = 90
    predictions_df['Tm(°C)'] = predictions_df['Predicted_Tm'] * (original_max - original_min) + original_min
    actual_tm = predictions_df.drop(['Predicted_Tm'], axis= 1)
    return actual_tm

def main():
    print('############################################################################################')
    print('# This program PPTStab is developed for designing of thermostable proteins with a desired melting temperature #')
    print('# developed by Prof G. P. S. Raghava group.               #')
    print('# Please cite: PPTStab; available at https://webs.iiitd.edu.in/raghava/pptstab/  #')
    print('############################################################################################')

    parser = argparse.ArgumentParser(description='Please provide following arguments')

    ## Read Arguments from command
    parser.add_argument("-i", "--input", type=str, required=True, help="Input: protein or peptide sequence(s) in FASTA format or single sequence per line in single letter code")
    parser.add_argument("-o", "--output",type=str, help="Output: File for saving results by default outfile.csv")
    parser.add_argument("-j", "--job",type=int, choices = [1,2], help="Job Type: 1:Predict, 2: Design, 3:Scan, by default 1")
    parser.add_argument("-f","--flag", type=float,required=True, help="Cell Flag: Value between 0 or 1 by default 1")
    parser.add_argument("-d","--display", type=int, choices = [1,2], help="Display: 1:Thermophilic proteins only, 2: All peptides, by default 1")
    parser.add_argument("-m","--method", type=str, choices = ['EMB','AAC','SER'], help="Display: EMB, SER, AAC")
    args = parser.parse_args()
    Sequence= args.input        # Input variable
    if args.output == None:
        result_filename= "outfile.csv"
    else:
        result_filename = args.output
    if args.flag == None:
            Flag = int(1)
    else:
            Flag= float(args.flag)
    if args.job == None:
            Job = int(1)
    else:
            Job = int(args.job)
    if args.display == None:
            dplay = int(1)
    else:
            dplay = int(args.display)
    if args.method == None:
        Method = 'SER'
    else:
        Method = args.method
    #======================= Prediction Module start from here =====================
    if Method == 'EMB':
        if Job == 1:
            print('\n======= Thanks for using EMB Predict module of PPTStab =======\n')
            df_2,dfseq = readseq(Sequence)
            df1 = lenchk(dfseq)
            df11 = embedd_extract(df1)
            X = process_embedd(df11, Flag)
            mlres = model_run(X, nf_path+'/../models/emb_model/ann_model.onnx',nf_path+'/../models/emb_model/mlp_regressor.pkl')
            df44 = mlres.round(3)
            df55 = pd.concat([df_2,df44,dfseq], axis =1)
            df55.columns = ['seq_ID','Tm(°C)','Sequence']
            df55.to_csv(result_filename, index = None)
            print("\n=========Process Completed. Have an awesome day ahead. Your results will be stored in file :",result_filename,"=============\n")
        if Job ==2:
            print('\n======= Thanks for using EMB Design module of PPTStab.  =====\n')
            df_2,dfseq = readseq(Sequence)
            df1 = lenchk(dfseq)
            df_1 = mutants(df1,df_2)
            dfseq = df_1[['Seq']]
            df11 = embedd_extract(dfseq)
            X = process_embedd(df11, Flag)
            mlres = model_run(X, nf_path+'/../models/emb_model/ann_model.onnx',nf_path+'/../models/emb_model/mlp_regressor.pkl')
            df44 = mlres.round(3)
            df44 = mlres.round(3)
            df55 = pd.concat([df_1,mlres], axis =1)
            df55.to_csv(result_filename, index = None)
            print("\n=========Process Completed. Have an awesome day ahead. Your results will be stored in file :",result_filename,"=============\n")
    #===================== Design Model Start from Here ======================
    if Method == 'SER':
        if Job == 1:
            print('\n======= Thanks for using SER Predict module of PPTStab. =========\n')
            df_2,dfseq = readseq(Sequence)
            df1 = lenchk(dfseq)
            X = feature_ser_gen(df1, Flag)
            mlres = model_run(X, nf_path+'/../models/ser_model/ann_model.onnx',nf_path+'/../models/ser_model/mlp_regressor.pkl')
            df44 = mlres.round(3)
            df55 = pd.concat([df_2,df44,dfseq], axis =1)
            df55.columns = ['seq_ID','Tm(°C)','Sequence']
            df55.to_csv(result_filename, index = None)
            print("\n=========Process Completed. Have an awesome day ahead. Your results will be stored in file :",result_filename,"=============\n")
        if Job ==2:
            print('\n======= Thanks for using SER Design module of PPTStab.  ========\n')
            df_2,dfseq = readseq(Sequence)
            df1 = lenchk(dfseq)
            df_1 = mutants(df1,df_2)
            dfseq = df_1[['Seq']]
            X = feature_ser_gen(dfseq, Flag)
            mlres = model_run(X, nf_path+'/../models/ser_model/ann_model.onnx',nf_path+'/../models/ser_model/mlp_regressor.pkl')
            df44 = mlres.round(3)
            df55 = pd.concat([df_1,mlres], axis =1)
            df55.to_csv(result_filename, index = None)
            print("\n=========Process Completed. Have an awesome day ahead. Your results will be stored in file :",result_filename,"=============\n")

    #===================== Design Model Start from Here ======================
    if Method == 'AAC':
        if Job == 1:
            print('\n======= Thanks for using AAC Predict module of PPTStab.  =======\n')
            df_2,dfseq = readseq(Sequence)
            df1 = lenchk(dfseq)
            X = feature_aac_gen(df1, Flag)
            mlres = model_run(X, nf_path+'/../models/aac_model/ann_model.onnx',nf_path+'/../models/aac_model/mlp_regressor.pkl')
            df44 = mlres.round(3)
            df55 = pd.concat([df_2,df44,dfseq], axis =1)
            df55.columns = ['seq_ID','Tm(°C)','Sequence']
            df55.to_csv(result_filename, index = None)
            print("\n=========Process Completed. Have an awesome day ahead. Your results will be stored in file :",result_filename," =============\n")
        if Job ==2:
            print('\n======= Thanks for using AAC Design module of PPTStab.  =====\n')
            df_2,dfseq = readseq(Sequence)
            df1 = lenchk(dfseq)
            df_1 = mutants(df1,df_2)
            dfseq = df_1[['Seq']]
            X = feature_aac_gen(dfseq, Flag)
            mlres = model_run(X, nf_path+'/../models/aac_model/ann_model.onnx',nf_path+'/../models/aac_model/mlp_regressor.pkl')
            df44 = mlres.round(3)
            df55 = pd.concat([df_1,mlres], axis =1)
            df55.to_csv(result_filename, index = None)
            print("\n=========Process Completed. Have an awesome day ahead. Your results will be stored in file :",result_filename,"=============\n")
if __name__ == "__main__":
    main()