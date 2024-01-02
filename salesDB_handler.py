import os
import json
import numpy as np
import pandas as pd
import datetime
import time


class SalesDBHandler:

    def __init__(self, dbs_path='./dbs', db_name='5653713567', verbose=True):
        """ Creates a SalesDB_Handler object

            dbs_path: path to all dbs location
            db_name:  name for a specific db

            verbose: verbosity level
            """

        self.dbs_path = dbs_path
        self.db_name = db_name
        self.db_path = os.path.join(self.dbs_path, self.db_name)
        self.verbose = verbose

        # Filenames for private data and records
        self.db_priv_filename = 'private.json'
        self.db_rec_filename = 'sales_records.csv'

        # Check and create database path
        self.check_db_path()

        # Define columns and types for the sales records DataFrame
        self.rec_df_columns = ['date', 'product_title', 'quantity', 'unit_price', 'client_name', 'phone', 'city',
                               'status']
        self.rec_df_types = ['datetime64[ns]', 'str', 'int', 'float', 'str', 'object', 'str', 'str']

        return None

    def check_db_path(self):
        """ checks default folder structure.
            creates it if necessary.
            """

        if not os.path.exists(self.dbs_path):
            if self.verbose:
                print(' - DB_Handler.check_db_path: crating folder: {}'.format(self.dbs_path))
            os.mkdir(self.dbs_path)

        if not os.path.exists(self.db_path):
            if self.verbose:
                print(' - SalesDB_Handler.check_db_path: crating folder: {}'.format(self.db_path))
            os.mkdir(self.db_path)

    def set_private_data(self, private_data_d={}):
        """ Saves provate data
            private_data_d: private data to be saved
            """

        self.check_db_path()

        priv_path = os.path.join(self.db_path, self.db_priv_filename)
        to_save = json.dumps(private_data_d)
        with open(priv_path, 'w') as f:
            if self.verbose:
                print(' - SalesDB_Handler.set_private_data: writing file: {}'.format(priv_path))
            f.write(to_save)

        return None

    def get_private_data(self):
        """ returns private data
            """
        priv_path = os.path.join(self.db_path, self.db_priv_filename)

        if not os.path.exists(priv_path):
            if self.verbose:
                print(' - SalesDB_Handler.get_private_data: file not found: {}'.format(priv_path))
            return None

        with open(priv_path, 'r') as f:
            if self.verbose:
                print(' - SalesDB_Handler.get_private_data: reading file: {}'.format(priv_path))

            fl = f.read()

        private_data_d = json.loads(fl)
        return private_data_d

    def get_rec_df(self):
        """ reads or creates and return an Pandas DataFrame as rec database
            """

        csv_path = os.path.join(self.db_path, self.db_rec_filename)
        if self.verbose:
            print(' - SalesDB_Handler.get_rec_df: reading: {}'.format(csv_path))

        if os.path.exists(csv_path):
            rec_db = pd.read_csv(csv_path, index_col=0, parse_dates=[self.rec_df_columns[0]],
                                 dtype=dict(zip(self.rec_df_columns[1:], self.rec_df_types[1:])))
        else:
            rec_db = pd.DataFrame()
            for col, c_type in zip(self.rec_df_columns, self.rec_df_types):
                rec_db[col] = pd.Series(dtype=c_type)

        return rec_db

    def set_rec_df(self, rec_db):
        """ reads or creates and return an Pandas DataFrame as rec database
            """

        self.check_db_path()
        csv_path = os.path.join(self.db_path, self.db_rec_filename)

        if self.verbose:
            print(' - SalesDB_Handler.set_rec_df: saveing: {}'.format(csv_path))

        rec_db.to_csv(csv_path)

        return rec_db

    def add_sale_record(self, date=None, product_title=None, quantity=0, unit_price=0, client_name=None, phone=None,
                        city=None, status=None):
        """ Appends a record to rec_db. """
        quantity = int(quantity)
        unit_price = float(unit_price)  # Assuming unit_price is a decimal value
        status = str(status)

        rec_df = self.get_rec_df()

        if date is None:
            date = pd.to_datetime(datetime.datetime.now())
        else:
            date = pd.to_datetime(date)

        # Create a new DataFrame with the record to be added
        new_record = pd.DataFrame({
            self.rec_df_columns[0]: [date],
            self.rec_df_columns[1]: [product_title],
            self.rec_df_columns[2]: [quantity],
            self.rec_df_columns[3]: [unit_price],
            self.rec_df_columns[4]: [client_name],
            self.rec_df_columns[5]: [phone],
            self.rec_df_columns[6]: [city],
            self.rec_df_columns[7]: [status]
        })

        # Concatenate the existing DataFrame and the new DataFrame
        rec_df = pd.concat([rec_df, new_record], ignore_index=True)

        if self.verbose:
            print(' - SalesDB_Handler.add_record: after: \n {}'.format(rec_df))

        # Save the updated DataFrame
        self.set_rec_df(rec_df)

        return rec_df

    def delete_db(self):
        """ deletes all db files.
            """

        if os.path.exists(self.db_path):
            for f in os.listdir(self.db_path):
                to_rm = os.path.join(self.db_path, f)
                if self.verbose:
                    print(' - SalesDB_Handler.delete_db: deleting file: {}'.format(to_rm))
                os.remove(to_rm)

            if self.verbose:
                print(' - SalesDB_Handler.delete_db: deleting folder: {}'.format(self.db_path))
            os.rmdir(self.db_path)

            # we must wait to the OS to prevent some errors
            time.sleep(0.1)
        return None

    def get_stats(self, last_n_days=7):
        """ Return a list of revenues, quantities sold, and average prices for each product category.
        """
        df = self.get_rec_df()
        df_f = df[df.date > datetime.datetime.now() - datetime.timedelta(days=last_n_days)]

        if len(df_f) == 0:
            # No sales entries in the specified period
            return ["Sorry {name}, you don't have any sales entries yet. Please make a sale before asking for stats."]

        gs = df_f.groupby('product_title')
        stats_list = []

        for k in gs.groups.keys():
            df_g = gs.get_group(k)
            total_revenue = (df_g[self.rec_df_columns[2]] * df_g[self.rec_df_columns[3]]).sum()
            average_price = df_g[self.rec_df_columns[3]].mean()
            total_quantity = df_g[self.rec_df_columns[2]].sum()

            stats_list.append({
                'product_category': str(k),
                'n_records': last_n_days,
                'total_revenue': total_revenue,
                'average_price': average_price,
                'total_quantity_sold': total_quantity,
            })

        return stats_list


if __name__ == '__main__':
    # Example usage for sales records

    sales_dbh = SalesDBHandler(verbose=True)

    for i in range(1):
        # Add a sales record with unit price
        sales_dbh.add_sale_record(product_title='ST-901', quantity=5, unit_price=20.0, client_name='John Doe',
                                  phone='1234567890', city='New York', status='Paid')
        # Display the sales records DataFrame
        print(sales_dbh.get_rec_df())

        # Get statistics for the last 5 days
        print(sales_dbh.get_stats(last_n_days=5))