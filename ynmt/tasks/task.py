#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) Jason Young (杨郑鑫).
#
# E-Mail: <AI.Jason.Young@outlook.com>
# 2020-09-10 15:02
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


from ynmt.data.dataset import Dataset

from ynmt.utilities.file import mk_temp, rm_temp, load_data, load_datas, dump_data, dump_datas
from ynmt.utilities.multiprocessing import multi_process


class Task(object):
    def __init__(self, logger, structure):
        self.logger = logger
        self.structure = structure

    @classmethod
    def setup(cls, args):
        raise NotImplementedError

    def load_ancillary_datasets(self, args):
        raise NotImplementedError

    def build_ancillary_datasets(self, args):
        raise NotImplementedError

    def training_batches(self, args):
        raise NotImplementedError

    def validation_batches(self, args):
        raise NotImplementedError

    def testing_batches(self, args):
        raise NotImplementedError

    def build_datasets(self, args):
        def produce_dataset(semi_dataset_paths, shard_size):
            # Produce dataset(which is made up of dataset shards) from semi-datasets
            dataset = Dataset(self.structure)
            for semi_dataset_path in semi_dataset_paths:
                semi_dataset = load_data(semi_dataset_path)
                for instance in semi_dataset:
                    if len(dataset) == shard_size:
                        yield dataset
                        dataset = Dataset(self.structure)
                    else:
                        dataset.add(instance)
            if len(dataset) != 0:
                yield dataset

        # 1. Build Training Dataset
        self.logger.info(f'Building training dataset ...')
        self.logger.info(f' * Raw Data will be aligned and partitioned, several semi-datasets with size of {args.work_amount} will be generated.')
        training_semi_dataset_paths = multi_process(
            self.build_semi_dataset,
            self.align_and_partition_raw_data(args.raw_data.training, args.work_amount),
            args.number_worker
        )
        self.logger.info(f'   The construction of semi-datasets is complete.')

        self.logger.info(f' * Producing Dataset with shard size of {args.shard_size} ...')
        training_dataset = produce_dataset(training_semi_dataset_paths, args.shard_size)
        self.logger.info(f'   The construction of dataset is complete.')

        self.logger.info(f' > Saving Training Dataset to {args.datasets.training} ...')
        dump_datas(args.datasets.training, training_dataset)
        self.logger.info(f'   Training Dataset has been saved.')

        self.logger.info(f' - Removing semi-dataset ...')
        for training_semi_dataset_path in training_semi_dataset_paths:
            rm_temp(training_semi_dataset_path)
        self.logger.info(f'   Finished removing semi-dataset.')

        # 2. Build Validation Dataset
        self.logger.info(f'Building validation dataset ...')
        self.logger.info(f' * Raw Data will be aligned and partitioned, several semi-datasets with size of {args.work_amount} will be generated.')
        validation_semi_dataset_paths = multi_process(
            self.build_semi_dataset,
            self.align_and_partition_raw_data(args.raw_data.validation, args.work_amount),
            args.number_worker
        )
        self.logger.info(f'   The construction of semi-datasets is complete.')

        self.logger.info(f' * Producing Dataset with shard size of {args.shard_size} ...')
        validation_dataset = produce_dataset(validation_semi_dataset_paths, args.shard_size)
        self.logger.info(f'   The construction of dataset is complete.')

        self.logger.info(f' > Saving Validation Dataset to {args.datasets.validation} ...')
        dump_datas(args.datasets.validation, validation_dataset)
        self.logger.info(f'   Validation Dataset has been saved.')

        self.logger.info(f' - Removing semi-dataset ...')
        for validation_semi_dataset_path in validation_semi_dataset_paths:
            rm_temp(validation_semi_dataset_path)
        self.logger.info(f'   Finished removing semi-dataset.')

    def build_semi_dataset(self, aligned_raw_data_partition):
        semi_dataset = Dataset(self.structure)

        for aligned_raw_data_item in zip(*aligned_raw_data_partition):
            instance = self.build_instance(aligned_raw_data_item)
            semi_dataset.add(instance)

        semi_dataset_path = mk_temp('ynmt-datasets_', temp_type='file')
        dump_data(semi_dataset_path, semi_dataset)

        return semi_dataset_path

    def align_and_partition_raw_data(self, raw_data_args, partition_size):
        raise NotImplementedError

    def build_instance(self, aligned_raw_data_item):
        raise NotImplementedError