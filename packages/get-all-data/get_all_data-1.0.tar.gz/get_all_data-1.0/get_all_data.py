import pandas as pd

mail_df = pd.read_excel("test_data_email.xlsx").fillna("").astype({'日志ID': str}).set_index('日志ID').to_dict('index')
edr_df = pd.read_excel("test_data_edr.xlsx").fillna("").astype({'日志ID': str}).set_index('日志ID').to_dict('index')
dns_df = pd.read_excel("test_data_dns.xlsx").fillna("").astype({'日志ID': str}).set_index('日志ID').to_dict('index')
attack_chain_df = pd.read_excel("output_res_three_chains(2).xlsx")

def get_data(log_id, log_dict):
    if isinstance(log_id, str) and ',' in log_id:
        datas = []
        ids = [id_.strip('" ') for id_ in log_id.split(',')]
        for id_ in ids:
            domain = log_dict.get(id_,{}).get('domain')
            if domain not in datas:
                datas.append(domain)
        return datas
    else:
        return [log_dict.get(log_id,{}).get('domain')]

def get_domain(edr_cmd, edr_cmd_chain, dns_content):
    for domain in dns_content:
        domain = domain.lower()
        if domain in edr_cmd:
            return True
        elif domain in edr_cmd_chain:
            return True
    return False

results = []
for index, rows in attack_chain_df.iterrows():
    work_id = rows['工号']
    mail_id = str(rows['email日志ID'])
    edr_id = str(rows['edr日志ID'])
    dns_ids = rows['dns日志ID']
    mail_date = mail_df.get(mail_id,{}).get('时间')
    mail_subject = mail_df.get(mail_id,{}).get('subject')
    mail_content = mail_df.get(mail_id,{}).get('context')
    mail_attachment = mail_df.get(mail_id,{}).get('attachment')
    edr_date = edr_df.get(edr_id,{}).get('时间')
    edr_cmd = edr_df.get(edr_id,{}).get('cmd')
    edr_cmd_chain = edr_df.get(edr_id,{}).get('cmd_chain')
    dns_content = get_data(dns_ids, dns_df)
    domain_in_cmd = get_domain(edr_cmd, edr_cmd_chain, dns_content)
    results.append({
        "工号":work_id,
        "mail_id": mail_id,
        "edr_id": edr_id,
        "dns_ids": dns_ids,
        "mail_date": mail_date,
        "mail_subject": mail_subject,
        "mail_content": mail_content,
        "mail_attachment": mail_attachment,
        "edr_date": edr_date,
        "edr_cmd": edr_cmd,
        "edr_cmd_chain": edr_cmd_chain,
        "dns_content": dns_content,
        "domain_in_cmd": domain_in_cmd
    })

result_df = pd.DataFrame(results)
result_df.to_excel('output_res_three_chains_2.xlsx', index=False)
print("验证完成! 结果已保存到 attack_chain_all_data_results.xlsx")