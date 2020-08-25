#!/usr/bin/env python
# coding: utf-8


from models_bi.eta_metric_all import EtaMetricAll


def main():
    print('EtaMetricAll={}'.format(EtaMetricAll().create_if_not_exists()))
    pass


if __name__ == '__main__':
    main()