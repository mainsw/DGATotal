import whois
import socket

def get_whois(domain):
    try:
        query = whois.whois(domain)
        # assert isinstance(query, whois._3_adjust.Domain)
        if isinstance(query.expiration_date, list):
            query.update(expiration_date=query.expiration_date[-1])
        if isinstance(query.creation_date, list):
            query.update(creation_date=query.creation_date[-1])
        if isinstance(query.updated_date, list):
            query.update(updated_date=query.updated_date[-1])
        # domainIP = socket.gethostbyname(domain)
        return query
    except:
        pass
    return None

def get_ip(domain):
    domainIP = socket.gethostbyname(domain)
    return domainIP

def get_scans(domain):
    url = "http://" + domain
    urls = [url]
    scans = vt.get_url_reports([url])[url]['scans']

    positive, negative = [], []

    for key, val in scans.items():
        if val["detected"]:
            negative.append(key)
        else:
            positive.append(key)

    return positive, negative, len(positive), len(negative)


if __name__ == '__main__':
    # print('test domain: microsoft.com')
    # print(get_whois('microsoft.com'))
    # print(get_scans('pxxfmjhosgqqs.com'))
    pass