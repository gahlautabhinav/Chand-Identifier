# train/train_token.py
import os, argparse
from datasets import load_dataset, DatasetDict, ClassLabel
from transformers import AutoTokenizer, AutoModelForTokenClassification, TrainingArguments, Trainer
import numpy as np
from sklearn.metrics import precision_recall_fscore_support, accuracy_score
import json

LABELS = ['L', 'G']
LABEL2ID = {l:i for i,l in enumerate(LABELS)}
ID2LABEL = {i:l for l,i in LABEL2ID.items()}

def tokenize_and_align_labels(example, tokenizer, max_length=256):
    words = example['syllables']
    label_words = example['labels']
    enc = tokenizer(words, is_split_into_words=True, truncation=True, padding='max_length', max_length=max_length)
    word_ids = enc.word_ids()
    aligned_labels = []
    prev_word = None
    for wid in word_ids:
        if wid is None:
            aligned_labels.append(-100)
        elif wid != prev_word:
            aligned_labels.append(LABEL2ID[label_words[wid]])
            prev_word = wid
        else:
            aligned_labels.append(-100)
    enc['labels'] = aligned_labels
    return enc

def compute_metrics(pred):
    labels = pred.label_ids
    preds = np.argmax(pred.predictions, axis=-1)
    true_labels = []
    true_preds = []
    for l, p in zip(labels, preds):
        for (lab, pr) in zip(l, p):
            if lab != -100:
                true_labels.append(ID2LABEL[lab])
                true_preds.append(ID2LABEL[pr])
    p, r, f1, _ = precision_recall_fscore_support(true_labels, true_preds, labels=LABELS, average='macro', zero_division=0)
    acc = accuracy_score(true_labels, true_preds)
    return {"precision": p, "recall": r, "f1": f1, "accuracy": acc}

def main(args):
    # load jsonl. Expect columns: syllables (list), labels (list)
    ds = load_dataset('json', data_files={'train': args.train, 'validation': args.valid})
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer, use_fast=True)

    def tok_align(ex):
        return tokenize_and_align_labels(ex, tokenizer, max_length=args.max_len)

    tokenized = ds.map(tok_align, remove_columns=ds['train'].column_names)

    model = AutoModelForTokenClassification.from_pretrained(args.model_init, num_labels=len(LABELS))
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        num_train_epochs=args.epochs,
        logging_steps=50,
        evaluation_strategy='epoch' if args.eval else 'no',
        save_strategy='epoch',
        save_total_limit=2,
        weight_decay=0.01,
        push_to_hub=False,
    )
    trainer = Trainer(model=model, args=training_args, train_dataset=tokenized['train'], eval_dataset=tokenized['validation'] if args.valid else None, compute_metrics=compute_metrics)
    trainer.train()
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    print("Saved model & tokenizer to", args.output_dir)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--train', required=True)
    ap.add_argument('--valid', required=False)
    ap.add_argument('--output_dir', default='model_token')
    ap.add_argument('--tokenizer', default='ai4bharat/indic-bert')
    ap.add_argument('--model_init', default='ai4bharat/indic-bert')
    ap.add_argument('--batch_size', type=int, default=4)
    ap.add_argument('--epochs', type=int, default=2)
    ap.add_argument('--max_len', type=int, default=256)
    ap.add_argument('--eval', action='store_true')
    args = ap.parse_args()
    main(args)
