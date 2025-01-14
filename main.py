import torch
import time
from data import load_dataset
from models import StyleTransformer, Discriminator
from train import train, auto_eval


class Config():
    data_path = './data/amazon35/'
    log_dir = 'runs/exp'
    dataName = 'amazon35'
    save_path = '/kaggle/working'
    pretrained_embed_path = './embedding/'
    device = torch.device('cuda' if True and torch.cuda.is_available() else 'cpu')
    discriminator_method = 'Multi' # 'Multi' or 'Cond'
    load_pretrained_embed = False
    min_freq = 3
    max_length = 16
    embed_size = 256
    d_model = 256
    h = 4
    num_styles = 2
    num_classes = num_styles + 1 if discriminator_method == 'Multi' else 2
    num_layers = 4
    batch_size = 64
    lr_F = 0.0001
    lr_D = 0.0001
    L2 = 0
    iter_D = 10
    iter_F = 5
    F_pretrain_iter = 500
    log_steps = 5
    eval_steps = 25
    learned_pos_embed = True
    dropout = 0
    drop_rate_config = [(1, 0)]
    temperature_config = [(1, 0)]
    twoStepTuned = True
    threshould = 0.5

    slf_factor = 0.25
    cyc_factor = 0.5
    adv_factor = 1

    inp_shuffle_len = 0
    inp_unk_drop_fac = 0
    inp_rand_drop_fac = 0
    inp_drop_prob = 0


def main():
    config = Config()
    train_iters, dev_iters, test_iters, vocab = load_dataset(config)
    print('Vocab size:', len(vocab))
    model_F = StyleTransformer(config, vocab).to(config.device)
    model_D = Discriminator(config, vocab).to(config.device)
    print(config.discriminator_method)

    pretrained_F_dict = torch.load('/kaggle/input/add-embedding/style-transformer-master/yelp_glove200_F.pth')
    pretrained_D_dict = torch.load('/kaggle/input/add-embedding/style-transformer-master/yelp_glove200_D.pth')

    #  load generator - yelp pretrain model
    model_F_dict = model_F.state_dict()
    pretrained_F_dict = {k: v for k, v in pretrained_F_dict.items() if 'generator' not in k and 'embed' not in k}
    model_F_dict.update(pretrained_F_dict)
    model_F.load_state_dict(model_F_dict)

    model_F.encoder.requires_grad_(False)
    model_F.decoder.requires_grad_(False)
    model_F.decoder.generator.requires_grad_(True)
    # model_F.embed.token_embed.requires_grad_(True)
    model_F.to(config.device)

    model_D_dict = model_D.state_dict()
    pretrained_D_dict = {k: v for k, v in pretrained_D_dict.items() if k.startswith('embed') == False}
    model_D_dict.update(pretrained_D_dict)
    model_D.load_state_dict(model_D_dict)

    model_D.encoder.requires_grad_(False)
    model_D.to(config.device)
    
    train(config, vocab, model_F, model_D, train_iters, dev_iters, test_iters)

if __name__ == '__main__':
    main()
