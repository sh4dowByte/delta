import requests
import json

from app.utils.style import Colors

from rich.tree import Tree

class CWEFetcher:
    headers = {
        'accept': '*/*',
        'content-type': 'application/json',
        'origin': 'https://hackerone.com',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
        'x-csrf-token': 'ZXDBFgGe9S0KSqLHhtiEL1dhKtXoMMdS71LdQGmUDEVKp5Y8Mnf8F374aA6kur6NoInW+gJAYulCVkh75oWwDQ==',
        'x-product-area': 'hacktivity',
        'x-product-feature': 'cwe_discovery'
    }

    @staticmethod
    def fetch(search_term):
        payload = {
            "query": """
            query CweEntriesQuery($first: Int, $after: String, $last: Int, $before: String, $search: String, $offset: Int) {
              cwe_entries(
                order_by: {field: submission_count, direction: DESC}
                first: $first
                after: $after
                last: $last
                before: $before
                search: $search
                offset: $offset
              ) {
                edges {
                  node {
                    id
                    cwe_id
                    cwe_name
                    submission_count
                    submission_count_trailing_12_weeks
                  }
                }
                total_count
                pageInfo {
                  hasNextPage
                  endCursor
                  hasPreviousPage
                  startCursor
                }
              }
            }
            """,
            "variables": {
                "first": 25,
                "offset": 0,
                "search": search_term
            }
        }
        
        response = requests.post(HackerOne.url, headers=CWEFetcher.headers, data=json.dumps(payload))
        return response.json()


class CVEFetcher:
    headers = {
        'accept': '*/*',
        'content-type': 'application/json',
        'origin': 'https://hackerone.com',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
        'x-csrf-token': 'ZXDBFgGe9S0KSqLHhtiEL1dhKtXoMMdS71LdQGmUDEVKp5Y8Mnf8F374aA6kur6NoInW+gJAYulCVkh75oWwDQ==',
        'x-product-area': 'hacktivity',
        'x-product-feature': 'cve_discovery'
    }

    @staticmethod
    def fetch(search_term):
        payload = {
            "query": """
            query CveDataQuery($first: Int, $after: String, $last: Int, $before: String, $search: String, $offset: Int, $orderBy: AnalyticsOrderByInputType) {
              ranked_cve_entries(
                first: $first
                after: $after
                last: $last
                before: $before
                search: $search
                offset: $offset
                order_by: $orderBy
              ) {
                total_count
                pageInfo {
                  hasNextPage
                  endCursor
                  hasPreviousPage
                  startCursor
                }
                edges {
                  node {
                    id
                    cve_id
                    cve_description
                    rank
                    reports_submitted_count
                    products
                    vendors
                    epss
                  }
                }
              }
            }
            """,
            "variables": {
                "first": 25,
                "offset": 0,
                "search": search_term,
                "orderBy": {"key": "rank", "direction": "asc"}
            }
        }

        response = requests.post(HackerOne.url, headers=CVEFetcher.headers, data=json.dumps(payload))
        return response.json()

    @staticmethod
    def fetch_cve_detail(search_term):
        payload = {
            "operationName": "CveDiscoveryDetailedViewCveEntry",
            "query": """
              query CveDiscoveryDetailedViewCveEntry($cve_id: String!) {
                  cve_entry(cve_id: $cve_id) {
                      rank
                      reports_submitted_count
                      severity_count_unknown
                      severity_count_none
                      severity_count_low
                      severity_count_medium
                      severity_count_high
                      severity_count_critical
                      __typename
                  }
              }
            """,
            "variables": {
                "cve_id": search_term
            },
        }

        response = requests.post(HackerOne.url, headers=CVEFetcher.headers, data=json.dumps(payload))
        return response.json()


class HackerOne:
    url = "https://hackerone.com/graphql"
    
    @staticmethod
    def fetch_cwe(search_term, title = ''):
        data = CWEFetcher.fetch(search_term)
        datas = data['data']['cwe_entries']['edges']

        tree = Tree(title)

        for data in datas:
            node = data['node']
            data_node = tree.add(f"[green]{node["cwe_id"]}[/green]")
            data_node.add(f"Name        : {node['cwe_name']}")

            submission_node = data_node.add(f"📝 Submission")
            submission_node.add(f"Count    : {node['submission_count']}")
            submission_node.add(f"12 Weeks : {node['submission_count_trailing_12_weeks']}")

        if not datas:
          tree.add(f"[yellow]CWE not detected[/yellow]")

        return tree

    @staticmethod
    def fetch_cve(search_term, title = ''):
        data = CVEFetcher.fetch(search_term)
        datas = data['data']['ranked_cve_entries']['edges']

        tree = Tree(title)

        for data in datas:
            node = data['node']
            data_node = tree.add(f"[green]{node["cve_id"]}[/green]")
            data_node.add(f"Rank        : {node['rank']}")

            if node.get('epss'):
                data_node.add(f"EPSS        : {node['epss']}")

            if node.get('reported'):
                data_node.add(f"Reported    : {node['reported']}")

            if node.get('vendors'):
                vendors_node = data_node.add(f"Vendors")
                for ref in node['vendors']:
                    vendors_node.add(f"{ref}")

            if node.get('cve_description'):
                description_node = data_node.add(f"📝 Description")
                description_node.add(f"{node['cve_description'].replace('\\n\\n', '')}")

            if node.get('products'):
                products_node = data_node.add("📦 Products")
                for ref in node['products']:
                    products_node.add(f"{ref}")

        if not datas:
          tree.add(f"[yellow]CVE not detected[/yellow]")

        return tree

    @staticmethod
    def fetch_cve_detail(search_term, title = ''):
        data = CVEFetcher.fetch_cve_detail(search_term)
        datas = data['data']['cve_entry']

        tree = Tree(title)
        node = datas

        if datas:
          data_node = tree.add(f"[green]{search_term}[/green]")
          data_node.add(f"Rank        : {node['rank']}")
          data_node.add(f"Reports     : {node['reports_submitted_count']}")

          severity = data_node.add(f"Severity")
          severity.add(f"[cyan]Unknown[/cyan]     : {node['severity_count_unknown']}")
          severity.add(f"[green]None[/green]        : {node['severity_count_none']}")
          severity.add(f"[yellow]Low[/yellow]         : {node['severity_count_low']}")
          severity.add(f"[red]Medium[/red]      : {node['severity_count_medium']}")
          severity.add(f"[purple]High[/purple]        : {node['severity_count_high']}")
            
        if not datas:
          tree.add(f"[yellow]CVE not detected[/yellow]")

        return tree