import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats import multitest as multi


def calcu_hypergeom(gene_list_obj, gmt_obj, bg=None, min_count=1):
    allgenes = bg
    allgenes = len(gmt_obj.unique_genes)

    gene_list = gene_list_obj.gene_list
    subsets = sorted(gmt_obj.term_gene_dic.keys())

    # 创建一个列表来存储结果行
    rows = []
    for s in subsets:
        # each set
        category = gmt_obj.term_gene_dic.get(s)
        category = set(category)
        _geneset = len(category)

        # gene list
        gene_list = set(gene_list)
        # expr_genes = len(gene_list)
        expr_genes = len(gene_list.intersection(gmt_obj.unique_genes))

        # intersection
        hits = category.intersection(gene_list)
        expr_in_geneset = len(hits)
        if expr_in_geneset > min_count:
            pvalue = stats.hypergeom.sf(expr_in_geneset - 1, allgenes, _geneset, expr_genes)
            # oddsratio means the expr_in_geneset is greater than theory(>1) or lettle than theory(<1)
            pvalue_thred = 0.05
            if pvalue <= pvalue_thred:
                rows.append({
                    'Term': s,
                    'Term_name': gmt_obj.term_name[s],
                    'Adjusted P-value': pvalue
                })

        # 最后一次性创建DataFrame
    res = pd.DataFrame(rows) if rows else pd.DataFrame(columns=['Term', 'Adjusted P-value', 'Term_name'])
    #sort by 'Adjusted P-value'
    res = res.sort_values(by='Adjusted P-value', ascending=True)

    return res


def adj_pv(res: pd.DataFrame, ad_pth=0.05):
    pvs = multi.multipletests(np.array(res['Adjusted P-value']), alpha=0.05)
    res['Adjusted P-value'] = pvs[1]
    res = res.loc[res['Adjusted P-value'] <= ad_pth]
    return res


def hypergeom_single(expr_in_geneset, allgenes, _geneset, expr_genes, min_count=1):
    if expr_in_geneset <= min_count:
        pvalue = 1
    else:
        pvalue = stats.hypergeom.sf(expr_in_geneset - 1, allgenes, _geneset, expr_genes)
    return pvalue


def hypergeom_row(expr_in_genesets, allgenes, _geneset, expr_genes, min_count=2):
    each_gmt_pvalues = []
    for ih, value in enumerate(expr_in_genesets):
        expr_in_geneset = value
        expr_gene = expr_genes[ih]
        if expr_in_geneset <= min_count:
            pvalue = 1
        else:
            pvalue = stats.hypergeom.sf(expr_in_geneset - 1, allgenes, _geneset, expr_gene)
        each_gmt_pvalues.append(pvalue)
    return each_gmt_pvalues


def calcu_hypergeom_pp(gene_list_obj, gmt_obj, bg=None, min_count=1):
    allgenes = bg
    allgenes = len(gmt_obj.unique_genes)

    gene_list = gene_list_obj.gene_list
    subsets = sorted(gmt_obj.term_gene_dic.keys())

    res = pd.DataFrame(columns=['Term', 'Adjusted P-value', 'Term_name'])
    for s in subsets:
        # each set
        category = gmt_obj.term_gene_dic.get(s)
        category = set(category)
        _geneset = len(category)

        # gene list
        gene_list = set(gene_list)
        expr_genes = len(gene_list)

        # intersection
        hits = category.intersection(gene_list)
        expr_in_geneset = len(hits)
        if expr_in_geneset > min_count:
            pvalue = stats.hypergeom.sf(expr_in_geneset - 1, allgenes, _geneset, expr_genes)
            # oddsratio means the expr_in_geneset is greater than theory(>1) or lettle than theory(<1)
            pvalue_thred = 0.05
            if pvalue <= pvalue_thred:
                row = pd.DataFrame({
                    'Term': [s],
                    'Term_name': [gmt_obj.term_name[s]],
                    'Adjusted P-value': [pvalue]
                })
                res = pd.concat([res, row], ignore_index=True)
    return res
