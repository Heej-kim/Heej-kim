
import torch
import torch.nn as nn
import torch.nn.functional as F

import numpy as np

import random
class CustomCNN(nn.Module):
    def __init__(self):
        # NOTE: you can freely add hyperparameters argument
        super(CustomCNN, self).__init__()
        ##############################################################################
        #                          IMPLEMENT YOUR CODE                               #
        ##############################################################################
        # Problem1-1: define cnn model        

        self.conv_layer = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size = 7, padding = 3, stride = 1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
        )
        self.res1_layer = nn.Sequential(
            nn.Conv2d(32,64,kernel_size = 3, padding = 1, stride = 1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Conv2d(64,64,kernel_size = 3, padding = 1, stride = 1),
            nn.BatchNorm2d(64),
        )
        self.res2_layer = nn.Sequential(
            nn.Conv2d(64,128,kernel_size = 3, padding = 1, stride = 2),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.Conv2d(128,128,kernel_size = 3, padding = 1, stride = 1),
            nn.BatchNorm2d(128),
        )
        self.res3_layer = nn.Sequential(
            nn.Conv2d(128,128,kernel_size = 3, padding = 1, stride = 2),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.Conv2d(128,128,kernel_size = 3, padding = 1, stride = 1),
            nn.BatchNorm2d(128),
        )
        self.skip1 = nn.Sequential(
            nn.Conv2d(32,64,kernel_size = 1,bias = False),
            nn.BatchNorm2d(64),
        )
        self.skip2 = nn.Sequential(
            nn.Conv2d(64,128,kernel_size = 1, stride = 2,bias = False),
            nn.BatchNorm2d(128),
        )
        self.skip3 = nn.Sequential(
            nn.Conv2d(128,128,kernel_size = 1, stride = 2,bias = False),
            nn.BatchNorm2d(128),
        )
        self.Avgpool = nn.AdaptiveAvgPool2d((2,2))
        self.FC = nn.Sequential(
            nn.Linear(512,64),
        )
        self.ReLU = nn.Sequential(
            nn.ReLU(),
        )
        ##############################################################################
        #                          END OF YOUR CODE                                  #
        ##############################################################################

    def forward(self, inputs):
        """
        For reference (shape example)
        inputs: Batch size X (Sequence_length, Channel=1, Height, Width)
        outputs: (Sequence_length X Batch_size, Hidden_dim)
        """
        ##############################################################################
        #                          IMPLEMENT YOUR CODE                               #
        ##############################################################################
        # Problem1-2: code CNN forward path        
        outputs = self.conv_layer(inputs)
        #print("1st output: {} ".format(outputs.shape))
        
        outputs = self.skip1(outputs) + self.res1_layer(outputs)
        outputs = self.ReLU(outputs)
        outputs = self.skip2(outputs) + self.res2_layer(outputs)
        outputs = self.ReLU(outputs)
        outputs = self.skip3(outputs) + self.res3_layer(outputs)
        outputs = self.ReLU(outputs)
        
        outputs = self.Avgpool(outputs)
        
        #print("Avg pooled output: {} ".format(outputs.shape))
        #print(outputs.shape)
        
        outputs = outputs.view(outputs.shape[0],-1)
        outputs = self.FC(outputs)
        ##############################################################################
        #                          END OF YOUR CODE                                  #
        ##############################################################################
        return outputs

class LSTM(nn.Module):
    def __init__(self, input_dim, hidden_size, vocab_size, num_layers=1, dropout=0.0):
        super(LSTM, self).__init__()

        # define the properties
        self.input_dim = input_dim
        self.hidden_size = hidden_size
        self.vocab_size = vocab_size
        
        ##############################################################################
        #                          IMPLEMENT YOUR CODE                               #
        ##############################################################################
        # Problem2-1: Define lstm and input, output projection layer to fit dimension
        # output fully connected layer to project to the size of the class
        
        # you can either use torch LSTM or manually define it
        self.lstm = nn.LSTM(input_size=hidden_size, hidden_size=hidden_size, num_layers=num_layers, dropout=dropout)
        self.fc_in = nn.Linear(input_dim, hidden_size)
        self.fc_out = nn.Linear(hidden_size, vocab_size)
        
        ##############################################################################
        #                          END OF YOUR CODE                                  #
        ##############################################################################

    def forward(self, feature, h, c):
        """
        For reference (shape example)
        feature: (Sequence_length, Batch_size, Input_dim)
        """
        ##############################################################################
        #                          IMPLEMENT YOUR CODE                               #
        ##############################################################################
        # Problem2-2: Design LSTM model for letter sorting
        # NOTE: sequence length of feature can be various    
        #print("feature.shape : ", feature.shape)    #seqlen, 256, 64





        embed = self.fc_in(feature) #batch_size, max_seqlen, hidden_size
        #if seq_lengths is None:
        output, (h_next , c_next) = self.lstm(embed,(h,c))

        #else:
        #  packed = torch.nn.utils.rnn.pack_padded_sequence(embed, seq_lengths.cpu().numpy(), batch_first=True)
        #  #batch_size, 
        #  output, (h_next , c_next) = self.lstm(packed,(h,c))
        #  output, _ = torch.nn.utils.rnn.pad_packed_sequence(output)

        #output.shape = batch_size, max_seqlen, hidden_size
        output = self.fc_out(output)
        ##############################################################################
        #                          END OF YOUR CODE                                  #
        ##############################################################################
        
        # (sequence_lenth, batch, num_classes), (num_rnn_layers, batch, hidden_dim), (num_rnn_layers, batch, hidden_dim)
        return output, h_next, c_next  


class ConvLSTM(nn.Module):
    def __init__(self, sequence_length=None, num_classes=26, cnn_layers=None,
                 cnn_input_dim=1, rnn_input_dim=256,
                 cnn_hidden_size=256, rnn_hidden_size=512, rnn_num_layers=1, rnn_dropout=0.0,):
        # NOTE: you can freely add hyperparameters argument
        super(ConvLSTM, self).__init__()

        # define the properties, you can freely modify or add hyperparameters
        self.cnn_hidden_size = cnn_hidden_size
        self.rnn_hidden_size = rnn_hidden_size
        self.cnn_input_dim = cnn_input_dim
        self.rnn_input_dim = rnn_input_dim
        self.rnn_num_layers = rnn_num_layers
        self.sequence_length = sequence_length
        self.num_classes = num_classes
        ##############################################################################
        #                          IMPLEMENT YOUR CODE                               #
        ##############################################################################
        self.conv = CustomCNN()
        self.lstm = LSTM(rnn_input_dim,rnn_hidden_size,num_classes,rnn_num_layers,rnn_dropout)
        self.FC = nn.Linear(num_classes,rnn_input_dim).cuda()

        self.init_lstm = torch.nn.LSTM(input_size = rnn_hidden_size, hidden_size = rnn_hidden_size, num_layers= rnn_num_layers, dropout = rnn_dropout)
        # NOTE: you can define additional parameters
        ##############################################################################
        #                          END OF YOUR CODE                                  #
        ##############################################################################

    def forward(self, inputs):
        """
        input is (imgaes, labels) (training phase) or images (test phase)
        images: sequential features of Batch size X (Sequence_length, Channel=1, Height, Width)
        labels: Batch size X (Sequence_length)
        outputs should be a size of Batch size X (1, Num_classes) or Batch size X (Sequence_length, Num_classes)
        """






        # for teacher-forcing
        have_labels = False
        if len(inputs) == 2:
            have_labels = True
            images, labels = inputs
        else:
            images = inputs

        ##############################################################################
        #                          IMPLEMENT YOUR CODE                               #
        ##############################################################################
        # Problem3: input image into CNN and RNN sequentially.
        # NOTE: you can use teacher-forcing using labels or not
        # NOTE: you can modify below hint code 



        #images? batch size * (seqlen, 1, 28, 28)

        batch_size = len(images) 
        hidden_state = torch.zeros((self.rnn_num_layers, batch_size, self.rnn_hidden_size)).cuda()
        cell_state = torch.zeros((self.rnn_num_layers, batch_size, self.rnn_hidden_size)).cuda()
        
        ##seq_lengths = torch.tensor([images[i].shape[0] for i in range(0,len(images))])
        ##hidden_feature = [self.conv(image.cuda()) for image in images]  #batch_size * (seqlen * 64)
        hidden_feature = self.conv(images[0].cuda()).unsqueeze(1)
        #print(hidden_feature.shape) #1, seqlen, 64

        #sort in seq_lengths order
        ##seq_lengths, perm_idx = seq_lengths.sort(0,descending=True)
        #print("perm_idx : ",perm_idx)
        ##sorted_hidden = [hidden_feature[i] for i in perm_idx]  #sorted_hidden : torch.tensor(batch_size, max_seqlen, 64)

        ##if have_labels:
        ##  sorted_labels = [labels[i] for i in perm_idx] 
          


        #packed_hidden = torch.nn.utils.rnn.pad_sequence(sorted_hidden,padding_value = 0).permute(1,0,2)         #batch_size, seqlen,  64

        #LSTM input one by one.
        ##for i in range(0,len(hidden_feature)):
        ##  _, hidden_state, cell_state = self.lstm(hidden_feature[i].unsqueeze(0), hidden_state, cell_state)
        _, hidden_state, cell_state = self.lstm(hidden_feature, hidden_state, cell_state)
        
        #print(_.shape)
        #output.shape: seqlen_sum(all batch), hidden_size
        

        #output, hidden_state, cell_state = self.lstm(packed_hidden, hidden_state, cell_state,seq_lengths)
        #print("output of lstm shape:",output.shape)
        #outputs, hidden_state, cell_state =  self.lstm(hidden_feature,hidden_state,cell_state)
        
        start = torch.zeros(1,1,self.rnn_input_dim).cuda() #1, batch_size, self.num_classes
        out, hidden_state, cell_state = self.lstm(start,hidden_state,cell_state)     
        #out.shape = batch_size, max_seqlen, vocab_size

        ##outputs = torch.zeros(seq_lengths.max(), 1, self.num_classes)
        outputs = torch.zeros(images[0].shape[0], 1, self.num_classes)
        outputs[0] = out


        if have_labels:
            # training code ...
            #rnn_input = torch.nn.utils.rnn.pad_sequence(out) # for variable length batch ...
            #print("rnn_input.shape " ,rnn_input.shape)
            #pad_sequence : find longest sequence and padding all.
            #labels = torch.stack(labels).cuda()
            #print("len:", len(labels), labels[0].shape)
            labels = labels[0].reshape(1, len(images[0]) + 1, -1).permute(1,0,2)
            #labels : batch_size * (seqlen)
            ##labels = sorted_labels.reshape(batch_size,seq_lengths.max() + 1,-1).permute(1,0,2)
            #label : batch_size * (seq_lengths)
            """
            label_list = [[] for i in range(0,seq_lengths.max())]
            print(len(label_list))
          

            for i in range(0,len(labels)):
              for j in range(0, labels[i].shape[0]):
                print(i, j)
                label_list[j-1].append(labels[i][j])
            """
            #want? seqlen, batch_size
            #how?

            teacher_forcing_ratio = 0.5
            out = self.FC(out)        
#            for t in range(0,seq_lengths.max() - 1):
            for t in range(0, len(images[0])-1):
                out, hidden_state, cell_state = self.lstm(out,hidden_state,cell_state)
                outputs[t+1] = out
                teacher_force = random.random() < teacher_forcing_ratio
                if teacher_force:
                    out = labels[t].reshape(-1) #ex. tensor([11, 13, 15, 17])
                    #print("out_1 ", out)
                    out = F.one_hot(out.to(torch.int64),self.num_classes).unsqueeze(0)
                    #print("out_2 ", out)
                    out = out.float().cuda()
                    #print("out_3 ", out)

                    out = self.FC(out)
                else:
                    out = out.argmax(-1).reshape(-1)  
                    #print(out)          
                    out = F.one_hot(out,self.num_classes).unsqueeze(0)
                    out = out.float().cuda()
                    out = self.FC(out)    

        else:
            # evaluation code ...
            #rnn_input = torch.nn.utils.rnn.pad_sequence(out) # for variable length batch ...
            out = self.FC(out).cuda()
#            for t in range(0,seq_lengths.max() - 1):
            for t in range(0, len(images[0])-1):
                out, hidden_state, cell_state = self.lstm(out,hidden_state,cell_state)
                outputs[t+1] = out
                out = out.argmax(-1).reshape(-1)
                out = F.one_hot(out,self.num_classes).unsqueeze(0)
                out = out.float().cuda()
                out = self.FC(out)        

        #output.shape: seqlen_sum(all batch), hidden_size
        #print(outputs.shape)
        outputs = outputs.permute(1,0,2)
      


        #print("output shape in ConvLSTM", outputs.shape)

        outputs = [outputs[i] for i in range(outputs.shape[0])]
        
        ##############################################################################
        #                          END OF YOUR CODE                                  #
        ##############################################################################

        return outputs


