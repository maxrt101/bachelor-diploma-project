#!/usr/bin/env python3
from ultralytics import YOLO
import sys

default_model_name = 'yolov8n.yaml'
epochs = 300
batch = 32
export = 'ncnn'


def train_model(dataset: str, model_name: str | None = None):
    model_name = model_name if model_name else default_model_name

    print(f'Model: {model_name} epochs: {epochs}')

    model = YOLO(model_name)

    print(f'Train {dataset.split("/")[-2]}')

    model.train(
        data=dataset,
        epochs=epochs,
        device='cpu'
    )

    model.val()
    print(f'Export model {model_name}')
    model.export(format=export)


def export_model(model_name: str):
    print(f'Model: {model_name}')

    model = YOLO(model_name)

    model.val()
    print(f'Export model {model_name}')
    model.export(format=export)


def usage():
    print(
        'Usage: ./train.py COMMAND [ARGS...]\n'
        'Commands:\n'
        '    t|train DATASET [MODEL] - Train existing or new model\n'
        '    e|export MODEL          - Export model (path to best.pt)\n'
    )


def main():
    if len(sys.argv) < 3:
        usage()
        exit('Error: Invalid arguments')

    if sys.argv[1] in ['t', 'train']:
        train_model(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    elif sys.argv[1] in ['e', 'export']:
        export_model(sys.argv[2])
    else:
        usage()
        exit('Error: Invalid arguments')


if __name__ == '__main__':
    main()
