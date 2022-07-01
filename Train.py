import copy

import torch
import torchvision
import torch.nn as nn
from model import fine_tune_model
import DataLoad
import time
import torch.optim as optim
from torch.autograd import Variable


def train_model(data_loader, model, criterion, optimizer, lr_scheduler, num_epochs=25):
    """
    the pipeline of train PyTorch model
    :param data_loader:
    :param model:
    :param criterion:
    :param optimizer:
    :param lr_scheduler:
    :param num_epochs:
    :return:
    """
    since_time = time.time()

    best_model = model
    best_acc = 0

    for epoch in range(num_epochs):
        print('Epoch {}/{}'.format(epoch, num_epochs - 1))
        print('-' * 10)

        for phase in ['train', 'val']:
            if phase == 'train':
                optimizer = lr_scheduler(optimizer, epoch)
                model.train(True)  # Set model to training mode
            else:
                model.train(False)

            running_loss = 0.0
            running_corrects = 0

            for batch_data in data_loader.load_data(data_set=phase):
                inputs, labels = batch_data
                inputs, labels = Variable(inputs), Variable(labels)

                optimizer.zero_grad()

                outputs = model(inputs)
                _, predict = torch.max(outputs.data, 1)
                loss = criterion(outputs, labels)
                if phase == 'train':
                    loss.backward()
                    optimizer.step()

                # collect data info
                running_loss += loss.data[0]
                running_corrects += torch.sum(predict == labels.data)

            epoch_loss = running_loss / data_loader.data_sizes[phase]
            epoch_acc = running_corrects / data_loader.data_sizes[phase]

            print('{} Loss: {:.4f} Acc: {:.4f}'.format(
                phase, epoch_loss, epoch_acc))

            if phase == 'val' and epoch_acc > best_acc:
                best_acc = epoch_acc
                best_model = copy.deepcopy(model)

        print()

    time_elapsed = time.time() - since_time
    print('Training complete in {:.0f}m {:.0f}s'.format(
        time_elapsed // 60, time_elapsed % 60))
    print('Best val Acc: {:4f}'.format(best_acc))
    return best_model

def exp_lr_scheduler(optimizer, epoch, init_lr=0.001, lr_decay_epoch=7):
    """Decay learning rate by a factor of 0.1 every lr_decay_epoch epochs."""
    lr = init_lr * (0.1**(epoch // lr_decay_epoch))

    if epoch % lr_decay_epoch == 0:
        print('LR is set to {}'.format(lr))

    for param_group in optimizer.param_groups:
        param_group['lr'] = lr

    return optimizer

def save_torch_model(model, name):
    torch.save(model.state_dict(), name)



if __name__ == '__main__':
    train_dir = "data/TrainingSet/NIR"
    data_loader = DataLoad.loader(train_dir)


    # data_loader = DataLoader(data_dir='datasets/hymenoptera_data', image_size=IMAGE_SIZE, batch_size=4)
    inputs, classes = next(iter(data_loader.load_data()))
    out = torchvision.utils.make_grid(inputs)
    data_loader.show_image(out, title=[data_loader.data_classes[c] for c in classes])

    model = fine_tune_model()

    criterion = nn.CrossEntropyLoss()
    optimizer_ft = optim.SGD(model.parameters(), lr=0.001, momentum=0.9)
    try:
        model = train_model(data_loader, model, criterion, optimizer_ft, exp_lr_scheduler, num_epochs=25)
        save_torch_model(model, "model1")
    except KeyboardInterrupt:
        print('manually interrupt, try saving model for now...')
        save_torch_model(model, "model1")
        print('model saved.')

