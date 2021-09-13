# This script implements a version of the Anchor Calculator.
import pandas as pd
import streamlit as st

# from streamlit import caching
# caching.clear_cache()


@st.cache
def fetch_deposits():
    # use msg_events since it has more data than msgs
    deposits_one = 'https://api.flipsidecrypto.com/api/v2/queries/aedc094b-facc-4639-bf6e-15c822c2200f/data/latest'
    deposits_two = 'https://api.flipsidecrypto.com/api/v2/queries/6b7e0250-b328-4705-affd-affcbac16f52/data/latest'
    deposits_three = 'https://api.flipsidecrypto.com/api/v2/queries/409b2153-439d-4d2a-937e-c2915d68ebda/data/latest'
    deposits_four = 'https://api.flipsidecrypto.com/api/v2/queries/a4569f5e-b8b4-4067-8132-4660c1b85d63/data/latest'
    deposits_five = 'https://api.flipsidecrypto.com/api/v2/queries/2edd2feb-d633-4c09-ab4a-59b2b21a89eb/data/latest'

    deposits_one_df = pd.read_json(deposits_one)
    deposits_two_df = pd.read_json(deposits_two)
    deposits_three_df = pd.read_json(deposits_three)
    deposits_four_df = pd.read_json(deposits_four)
    deposits_five_df = pd.read_json(deposits_five)

    return pd.concat(
        [
            deposits_one_df,
            deposits_two_df,
            deposits_three_df,
            deposits_four_df,
            deposits_five_df
        ]
    )


@st.cache
def fetch_redemptions():
    # use msg_events to be consistent with its use in
    redemptions_one = 'https://api.flipsidecrypto.com/api/v2/queries/b478a812-520a-4b36-9b81-f1bb6a2ff70d/data/latest'
    redemptions_two = 'https://api.flipsidecrypto.com/api/v2/queries/a0a53bb6-3386-42cc-9e5d-567bb2c1ea3b/data/latest'
    redemptions_three = 'https://api.flipsidecrypto.com/api/v2/queries/24cdbf41-337e-4f97-b47e-b19b40fa92b8/data/latest'

    redemptions_one_df = pd.read_json(redemptions_one)
    redemptions_two_df = pd.read_json(redemptions_two)
    redemptions_three_df = pd.read_json(redemptions_three)

    return pd.concat(
        [
            redemptions_one_df,
            redemptions_two_df,
            redemptions_three_df
        ]
    )


@st.cache
def fetch_aust_transfers():
    transfers = 'https://api.flipsidecrypto.com/api/v2/queries/08b0b047-30e9-46dd-94f8-d684cbb2a9e3/data/latest'
    transfers_df = pd.read_json(transfers)
    return transfers_df


@st.cache
def fetch_mirror_collateral_deposits():
    collateral_deposits = \
        'https://api.flipsidecrypto.com/api/v2/queries/3ceed13a-b0c7-48ad-b0ef-aed2c8265306/data/latest'
    collateral_deposits_df = pd.read_json(collateral_deposits)
    return collateral_deposits_df


@st.cache
def fetch_mirror_collateral_withdraws():
    collateral_withdraws = \
        'https://api.flipsidecrypto.com/api/v2/queries/01ee8380-02ac-44d1-9aee-69ef49bcf8b1/data/latest'
    collateral_withdraws_df = pd.read_json(collateral_withdraws)
    return collateral_withdraws_df


@st.cache
def fetch_aust_price_table():
    aust_price = 'https://api.flipsidecrypto.com/api/v2/queries/988f6024-1cb2-4ac0-9c52-1c415fe7e0cd/data/latest'
    aust_price_df = pd.read_json(aust_price)
    return aust_price_df


def filter_deposits(deposits_df, depositor=None):
    if depositor:
        return deposits_df[deposits_df['DEPOSITOR'] == depositor]
    return deposits_df


def filter_redemptions(redemptions_df, redeemer=None):
    if redeemer:
        return redemptions_df[redemptions_df['REDEEMER'] == redeemer]
    return redemptions_df


def filter_aust_sent(transfers_df, sender=None):
    if sender:
        return transfers_df[transfers_df['SENDER'] == sender]
    return transfers_df


def filter_aust_received(transfers_df, receiver=None):
    if receiver:
        return transfers_df[transfers_df['RECEIVER'] == receiver]
    return transfers_df


def filter_mirror_collateral_deposits(collateral_deposits_df, depositor=None):
    if depositor:
        return collateral_deposits_df[collateral_deposits_df['SENDER'] == depositor]
    return collateral_deposits_df


def filter_mirror_collateral_withdraws(collateral_withdraws_df, withdrawer=None):
    if withdrawer:
        return collateral_withdraws_df[collateral_withdraws_df['SENDER'] == withdrawer]
    return collateral_withdraws_df


def find_closest_aust_pair(aust_price_df, other_df):
    combined_df = pd.merge_asof(
        other_df,
        aust_price_df.sort_values('BLOCK_ID'),
        on='BLOCK_ID',
        direction='nearest'
    )
    return combined_df


def compute_value_of_aust(
        df,
        aust_value_col,
        aust_amount_col,
        total_ust_value_col,
):
    df[total_ust_value_col] = df[aust_value_col] * df[aust_amount_col]
    return df


st.title('Anchor Calculator: The pieces of the puzzle')


st.subheader('aUST Value Table')
aust_price_df = fetch_aust_price_table()
st.write(aust_price_df)


st.subheader('Pick user')
user_address = st.text_input('User Address', value='terra1san7x37tn4zs09ufazgtyxf9h0ht9gm4t6qcdd')


st.subheader('Deposits')
deposits_df = fetch_deposits()
user_deposits = filter_deposits(deposits_df, depositor=user_address)
st.write(user_deposits)

total_deposits_ust = user_deposits['DEPOSIT_AMOUNT_UST'].sum(axis=0)
total_aust_minted = user_deposits['MINT_AMOUNT_AUST'].sum(axis=0)
st.write('Total user deposits (UST):', total_deposits_ust)
st.write('Total user mint (aUST):', total_aust_minted)


st.subheader('Redemptions')
redemptions_df = fetch_redemptions()
user_redemptions = filter_redemptions(redemptions_df, redeemer=user_address)
st.write(user_redemptions)

total_ust_redeemed = user_redemptions['UST_REDEEMED'].sum(axis=0)
total_aust_burnt = user_redemptions['AUST_BURNT'].sum(axis=0)
st.write('Total user redemptions (UST): ', total_ust_redeemed)
st.write('Total user aUST burnt: ', total_aust_burnt)

st.subheader('aUST Transfers')
transfers_df = fetch_aust_transfers()
aust_transfers_sent = filter_aust_sent(transfers_df, sender=user_address)
aust_transfers_received = filter_aust_received(transfers_df, receiver=user_address)

st.write('Transfers sent')
st.write(aust_transfers_sent)


st.write('Transfers sent with UST price')
aust_transfers_sent = find_closest_aust_pair(aust_price_df, aust_transfers_sent)
aust_transfers_sent = compute_value_of_aust(
    aust_transfers_sent,
    aust_amount_col='AUST_TRANSFERRED',
    aust_value_col='AVERAGED_AUST_VALUE',
    total_ust_value_col='UST_TRANSFERRED'
)
st.write(aust_transfers_sent)

total_aust_transfers_sent = aust_transfers_sent['AUST_TRANSFERRED'].sum(axis=0)
redemptions_via_transfers = aust_transfers_sent['UST_TRANSFERRED'].sum(axis=0)
st.write('Total aUST transferred out: ', total_aust_transfers_sent)
st.write('Total redemption value via transfers out: ', redemptions_via_transfers)


st.write('Transfers received')
st.write(aust_transfers_received)

aust_transfers_received = find_closest_aust_pair(aust_price_df, aust_transfers_received)
st.write('Transfers received with UST price')
aust_transfers_received = compute_value_of_aust(
    aust_transfers_received,
    aust_amount_col='AUST_TRANSFERRED',
    aust_value_col='AVERAGED_AUST_VALUE',
    total_ust_value_col='UST_TRANSFERRED'
)
st.write(aust_transfers_received)

total_aust_transfers_received = aust_transfers_received['AUST_TRANSFERRED'].sum(axis=0)
ust_deposits_via_transfers = aust_transfers_received['UST_TRANSFERRED'].sum(axis=0)
st.write('Total aUST transferred in: ', total_aust_transfers_received)
st.write('Total deposit value via transfers in: ', ust_deposits_via_transfers)


st.subheader('Mirror aUST Collateral Deposits')
collateral_deposits_df = fetch_mirror_collateral_deposits()
user_collateral_deposits_df = filter_mirror_collateral_deposits(
    collateral_deposits_df,
    depositor=user_address
)
st.write(user_collateral_deposits_df)

total_aust_collateralised = user_collateral_deposits_df['AUST_COLLATERALISED'].sum(axis=0)
st.write('Total aUST Collateralised: ', total_aust_collateralised)


st.subheader('Mirror aUST Collateral Withdraws')
collateral_withdraws_df = fetch_mirror_collateral_withdraws()
user_collateral_withdraws_df = filter_mirror_collateral_withdraws(
    collateral_withdraws_df,
    withdrawer=user_address
)
st.write(user_collateral_withdraws_df)

total_aust_withdrawn = \
    user_collateral_withdraws_df['AUST_COLLATERALISED'][
        user_collateral_withdraws_df['POSITION_TYPE'] == 'Withdraw from Borrow'
    ].sum(axis=0)
st.write('Total aUST Withdrawn: ', total_aust_withdrawn)

aust_lost_to_fees = user_collateral_withdraws_df[
    user_collateral_withdraws_df['POSITION_TYPE'] == 'Withdraw Protocol Fee'
]
st.write(aust_lost_to_fees)
aust_lost_to_fees = find_closest_aust_pair(
    aust_price_df=aust_price_df,
    other_df=aust_lost_to_fees
)
aust_lost_to_fees = compute_value_of_aust(
    aust_lost_to_fees,
    aust_amount_col='AUST_COLLATERALISED',
    aust_value_col='AVERAGED_AUST_VALUE',
    total_ust_value_col='UST_VALUE_COLLATERALISED'
)

total_aust_lost_to_fees = aust_lost_to_fees['AUST_COLLATERALISED'].sum(axis=0)
st.write('aUST lost to protocol fees:', total_aust_lost_to_fees)

total_ust_value_lost_to_fees = aust_lost_to_fees['UST_VALUE_COLLATERALISED'].sum(axis=0)
st.write('UST value of aUST lost to protocol fees: ', total_ust_value_lost_to_fees)

aust_liquidated = user_collateral_withdraws_df[
    user_collateral_withdraws_df['POSITION_TYPE'] == 'Liquidated aUST'
]
aust_liquidated = find_closest_aust_pair(
    aust_price_df=aust_price_df,
    other_df=aust_liquidated
)
aust_liquidated = compute_value_of_aust(
    aust_liquidated,
    aust_amount_col='AUST_COLLATERALISED',
    aust_value_col='AVERAGED_AUST_VALUE',
    total_ust_value_col='UST_VALUE_COLLATERALISED'
)
total_aust_liquidated = \
    user_collateral_withdraws_df['AUST_COLLATERALISED'][
        user_collateral_withdraws_df['POSITION_TYPE'] == 'Liquidated aUST'
     ].sum(axis=0)
st.write('aUST lost to liquidations:', total_aust_liquidated)
total_ust_liquidated = \
    aust_liquidated['UST_VALUE_COLLATERALISED'][
        aust_liquidated['POSITION_TYPE'] == 'Liquidated aUST'
        ].sum(axis=0)
st.write('UST lost to liquidations: ', total_ust_liquidated)

net_aust_lost = total_aust_liquidated + total_aust_lost_to_fees
net_aust_on_mirror = total_aust_collateralised - total_aust_withdrawn  - net_aust_lost
st.write('Net aUST on Mirror', net_aust_on_mirror)

st.subheader('Interest Calculation')

total_deposits_ust = total_deposits_ust + ust_deposits_via_transfers
st.write('Total Deposits UST: ', total_deposits_ust)
total_ust_redeemed = total_ust_redeemed + redemptions_via_transfers
st.write('Total Redemptions UST: ', total_ust_redeemed)

st.write('Total aUST minted: ', total_aust_minted)
st.write('Total aUST burnt: ', total_aust_burnt)
st.write('aUST on Mirror: ', net_aust_on_mirror)

net_aust_in_wallet = total_aust_minted - total_aust_burnt
net_aust_in_wallet = net_aust_in_wallet - net_aust_on_mirror - net_aust_lost
net_aust_in_wallet = net_aust_in_wallet - total_aust_transfers_sent + total_aust_transfers_received
st.write('aUST currently in wallet: ', net_aust_in_wallet)

current_aust_price = float(
    aust_price_df[aust_price_df['BLOCK_ID'] == aust_price_df['BLOCK_ID'].max()]['AVERAGED_AUST_VALUE']
)
current_wallet_aust_value = current_aust_price * net_aust_in_wallet
st.write('UST value of aUST in wallet: ', current_wallet_aust_value)

current_mirror_aust_value = current_aust_price * net_aust_on_mirror
st.write('UST value of aUST in Mirror: ', current_mirror_aust_value)

total_ust_value_of_aust_holdings = current_wallet_aust_value + current_mirror_aust_value
st.write('UST value of all aUST holdings: ', total_ust_value_of_aust_holdings)

interest_earned = total_ust_value_of_aust_holdings + total_ust_redeemed + \
                  total_ust_value_lost_to_fees - total_deposits_ust
interest_lost = total_ust_value_lost_to_fees + total_ust_liquidated
st.write('Total interest earned: ', interest_earned)
st.write('Value lost to liquidations + fees: ', interest_lost)








