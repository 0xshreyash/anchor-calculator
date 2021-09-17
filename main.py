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


@st.cache
def fetch_liquidation_transfer_back():
    liquidation_transfers = \
        'https://api.flipsidecrypto.com/api/v2/queries/cb6294ce-985a-4f8a-b6d2-43ea342e6969/data/latest'
    liquidation_transfer_dfs = pd.read_json(liquidation_transfers)
    return liquidation_transfer_dfs


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


def filter_aust_transfer_back(aust_transfer_back_df, owner=None):
    if owner:
        return aust_transfer_back_df[aust_transfer_back_df['OWNER'] == owner]
    return aust_transfer_back_df


def find_closest_aust_pair(aust_price_df, other_df):
    combined_df = pd.merge_asof(
        other_df.sort_values('BLOCK_ID'),
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


def show_aust_value_table():
    st.subheader('aUST Value Table')
    aust_price_df = fetch_aust_price_table()
    st.write(aust_price_df)
    return aust_price_df


def show_user_picker():
    st.subheader('Pick user')
    user_address = st.text_input('User Address', value='terra1san7x37tn4zs09ufazgtyxf9h0ht9gm4t6qcdd')
    return user_address


def show_user_deposits(user_address):
    st.subheader('Deposits')
    deposits_df = fetch_deposits()
    user_deposits = filter_deposits(deposits_df, depositor=user_address)
    st.write(user_deposits)
    total_deposits_ust = user_deposits['DEPOSIT_AMOUNT_UST'].sum(axis=0)
    total_aust_minted = user_deposits['MINT_AMOUNT_AUST'].sum(axis=0)
    st.write('Total user deposits (UST):', total_deposits_ust)
    st.write('Total user mint (aUST):', total_aust_minted)
    return user_deposits


def show_user_redemptions(user_address):
    st.subheader('Redemptions')
    redemptions_df = fetch_redemptions()
    user_redemptions = filter_redemptions(redemptions_df, redeemer=user_address)
    st.write(user_redemptions)

    total_ust_redeemed = user_redemptions['UST_REDEEMED'].sum(axis=0)
    total_aust_burnt = user_redemptions['AUST_BURNT'].sum(axis=0)
    st.write('Total user redemptions (UST): ', total_ust_redeemed)
    st.write('Total user aUST burnt: ', total_aust_burnt)
    return user_redemptions


def show_user_aust_transfers(user_address, aust_price_df):
    '''
    Note: This function only accounts for aUST transfers performed by the user
    '''
    st.subheader('aUST Transfers')
    transfers_df = fetch_aust_transfers()
    aust_transfers_sent = filter_aust_sent(transfers_df, sender=user_address)
    aust_transfers_received = filter_aust_received(transfers_df, receiver=user_address)

    #############################################################################################

    st.write('Transfers sent')

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

    #############################################################################################

    st.write('Transfers received')

    aust_transfers_received = find_closest_aust_pair(aust_price_df, aust_transfers_received)
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

    return aust_transfers_sent, aust_transfers_received


def mirror_collateral_deposits(user_address, aust_price_df):
    st.subheader('Mirror aUST Collateral Deposits')
    collateral_deposits_df = fetch_mirror_collateral_deposits()
    user_collateral_deposits_df = filter_mirror_collateral_deposits(
        collateral_deposits_df,
        depositor=user_address
    )
    user_collateral_deposits_df = find_closest_aust_pair(aust_price_df, user_collateral_deposits_df)
    user_collateral_deposits_df = compute_value_of_aust(
        user_collateral_deposits_df,
        aust_amount_col='AUST_COLLATERALISED',
        aust_value_col='AVERAGED_AUST_VALUE',
        total_ust_value_col='UST_VALUE_COLLATERALISED'
    )
    st.write(user_collateral_deposits_df)

    total_aust_collateralised = user_collateral_deposits_df['AUST_COLLATERALISED'].sum(axis=0)
    st.write('Total aUST Collateralised: ', total_aust_collateralised)
    return user_collateral_deposits_df


def mirror_collateral_withdrawn(user_address, aust_price_df):

    st.subheader('Mirror aUST Collateral Withdraws')

    collateral_withdraws_df = fetch_mirror_collateral_withdraws()
    all_collateral_withdraws = filter_mirror_collateral_withdraws(
        collateral_withdraws_df,
        withdrawer=user_address
    )

    st.write('aUST Collateral Withdraws: ', all_collateral_withdraws)

    user_collateral_withdraws_df = \
        all_collateral_withdraws[
            all_collateral_withdraws['POSITION_TYPE'] == 'Withdraw from Borrow'
        ]
    user_collateral_withdraws_df = find_closest_aust_pair(
        aust_price_df=aust_price_df,
        other_df=user_collateral_withdraws_df
    )
    user_collateral_withdraws_df = compute_value_of_aust(
        user_collateral_withdraws_df,
        aust_amount_col='AUST_COLLATERALISED',
        aust_value_col='AVERAGED_AUST_VALUE',
        total_ust_value_col='UST_VALUE_COLLATERALISED'
    )

    total_aust_withdrawn = user_collateral_withdraws_df['AUST_COLLATERALISED'].sum(axis=0)
    st.write('Total aUST Withdrawn: ', total_aust_withdrawn)

    aust_lost_to_fees = all_collateral_withdraws[
        all_collateral_withdraws['POSITION_TYPE'] == 'Withdraw Protocol Fee'
    ]
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
    st.write('Total aUST lost to protocol fees:', total_aust_lost_to_fees)

    total_ust_value_lost_to_fees = aust_lost_to_fees['UST_VALUE_COLLATERALISED'].sum(axis=0)
    st.write('UST value of aUST lost to protocol fees: ', total_ust_value_lost_to_fees)

    aust_liquidated = all_collateral_withdraws[
        all_collateral_withdraws['POSITION_TYPE'] == 'Liquidated aUST'
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
    total_aust_liquidated = aust_liquidated['AUST_COLLATERALISED'].sum(axis=0)
    st.write('aUST lost to liquidations:', total_aust_liquidated)
    total_ust_liquidated = \
        aust_liquidated['UST_VALUE_COLLATERALISED'].sum(axis=0)
    st.write('UST value lost to liquidations: ', total_ust_liquidated)

    # Find all transfers back to a user after an aUST liquidation
    aust_liquidation_transfer_back_df = fetch_liquidation_transfer_back()
    user_liq_aust_transfer_back_df = filter_aust_transfer_back(
        aust_liquidation_transfer_back_df, owner=user_address
    )
    user_liq_aust_transfer_back_df = find_closest_aust_pair(
        aust_price_df,
        user_liq_aust_transfer_back_df
    )
    user_liq_aust_transfer_back_df = compute_value_of_aust(
        user_liq_aust_transfer_back_df,
        aust_amount_col='AUST_TRANSFERRED_BACK',
        aust_value_col='AVERAGED_AUST_VALUE',
        total_ust_value_col='UST_VALUE_TRANSFERRED',
    )
    st.write('User\'s aUST transferred back due to liquidation', user_liq_aust_transfer_back_df)
    total_aust_transferred_back = user_liq_aust_transfer_back_df['AUST_TRANSFERRED_BACK'].sum(axis=0)
    st.write('Total aUST transferred back to user from Mirror: ', total_aust_transferred_back)

    return user_collateral_withdraws_df, aust_lost_to_fees, aust_liquidated, user_liq_aust_transfer_back_df


aust_price_df = show_aust_value_table()
user_address = show_user_picker()
user_deposits_df = show_user_deposits(user_address)
user_redemptions_df = show_user_redemptions(user_address)
user_transfers_sent_df, user_transfers_received_df = show_user_aust_transfers(user_address, aust_price_df)
user_collateral_deposits_df = mirror_collateral_deposits(user_address, aust_price_df)
user_collateral_withdraws_df, aust_lost_to_fees, aust_liquidated, aust_transferred_back = mirror_collateral_withdrawn(
    user_address, aust_price_df
)

total_aust_minted = user_deposits_df['MINT_AMOUNT_AUST'].sum(axis=0)
total_aust_redeemed = user_redemptions_df['AUST_BURNT'].sum(axis=0)
total_aust_collateralised = user_collateral_deposits_df['AUST_COLLATERALISED'].sum(axis=0)
total_aust_withdrawn = user_collateral_withdraws_df['AUST_COLLATERALISED'].sum(axis=0)
total_aust_lost_to_fees = aust_lost_to_fees['AUST_COLLATERALISED'].sum(axis=0)
total_aust_liquidated = aust_liquidated['AUST_COLLATERALISED'].sum(axis=0)
total_aust_transferred_back_in_liq = aust_transferred_back['AUST_TRANSFERRED_BACK'].sum(axis=0)
total_aust_transferred_in = user_transfers_received_df['AUST_TRANSFERRED'].sum(axis=0) - \
                                user_transfers_sent_df['AUST_TRANSFERRED'].sum(axis=0)

total_aust_in_wallet = total_aust_minted - total_aust_redeemed - total_aust_collateralised + total_aust_withdrawn \
                       + total_aust_transferred_back_in_liq + total_aust_transferred_in
total_aust_on_mirror = total_aust_collateralised - total_aust_withdrawn - total_aust_transferred_back_in_liq \
                       - total_aust_lost_to_fees - total_aust_liquidated

st.write('Total aUST in wallet: ', total_aust_in_wallet)
st.write('Total aUST on Mirror: ', total_aust_on_mirror)

total_aust_holdings = total_aust_in_wallet + total_aust_on_mirror
st.write('Total aUST Holdings: ', total_aust_holdings)
current_aust_price = float(
    aust_price_df[aust_price_df['BLOCK_ID'] == aust_price_df['BLOCK_ID'].max()]['AVERAGED_AUST_VALUE']
)
total_aust_holding_value_ust = total_aust_holdings * current_aust_price
st.write('Total UST value of aUST Holdings: ', total_aust_holding_value_ust)

total_ust_deposited = user_deposits_df['DEPOSIT_AMOUNT_UST'].sum(axis=0)
total_ust_transferred_in = user_transfers_received_df['UST_TRANSFERRED'].sum(axis=0)
total_ust_deposited += total_ust_transferred_in
st.write('Total UST deposited: ', total_ust_deposited)


total_ust_redeemed = user_redemptions_df['UST_REDEEMED'].sum(axis=0)
total_ust_value_transferred_out = user_transfers_sent_df['UST_TRANSFERRED'].sum(axis=0)
total_ust_paid_in_fees = aust_lost_to_fees['UST_VALUE_COLLATERALISED'].sum(axis=0)
total_ust_liquidated = aust_liquidated['UST_VALUE_COLLATERALISED'].sum(axis=0)

total_ust_redeemed += total_ust_value_transferred_out
total_ust_redeemed += total_ust_paid_in_fees
total_ust_redeemed += total_ust_liquidated

st.write('Total UST redeemed: ', total_ust_redeemed)

interest_earned = total_aust_holding_value_ust - total_ust_deposited + total_ust_redeemed
st.write('Total Interest Earned: ', interest_earned)

ust_lost = total_ust_paid_in_fees + total_ust_liquidated
st.write('Total UST lost: ', ust_lost)


#######################################################################################################


deposit_events_df = user_deposits_df.filter(['BLOCK_ID', 'MINT_AMOUNT_AUST', 'DEPOSIT_AMOUNT_UST'], axis=1)
deposit_events_df['Source'] = 'Void'
deposit_events_df['Destination'] = 'Wallet'
deposit_events_df.columns = ['BLOCK_ID', 'AUST_AMOUNT', 'UST_AMOUNT', 'Source', 'Destination']
st.write('Deposit Events: ', deposit_events_df)


redemption_events_df = user_redemptions_df.filter(['BLOCK_ID', 'AUST_BURNT', 'UST_REDEEMED'], axis=1)
redemption_events_df['Source'] = 'Wallet'
redemption_events_df['Destination'] = 'Void'
redemption_events_df.columns = ['BLOCK_ID', 'AUST_AMOUNT', 'UST_AMOUNT', 'Source', 'Destination']
st.write('Redemption Events: ', redemption_events_df)


collateral_deposit_events_df = user_collateral_deposits_df.filter(
    ['BLOCK_ID', 'AUST_COLLATERALISED', 'UST_VALUE_COLLATERALISED'],
    axis=1,
)
collateral_deposit_events_df['Source'] = 'Wallet'
collateral_deposit_events_df['Destination'] = 'Mirror'
collateral_deposit_events_df.columns = ['BLOCK_ID', 'AUST_AMOUNT', 'UST_AMOUNT', 'Source', 'Destination']
st.write('Collateral Deposit Events: ', collateral_deposit_events_df)


collateral_withdraw_events_df = user_collateral_withdraws_df.filter(
    ['BLOCK_ID', 'AUST_COLLATERALISED', 'UST_VALUE_COLLATERALISED'],
    axis=1,
)
collateral_withdraw_events_df['Source'] = 'Mirror'
collateral_withdraw_events_df['Destination'] = 'Wallet'
collateral_withdraw_events_df.columns = ['BLOCK_ID', 'AUST_AMOUNT', 'UST_AMOUNT', 'Source', 'Destination']
st.write('Collateral Withdraw Events: ', collateral_withdraw_events_df)


collateral_fee_events_df = aust_lost_to_fees.filter(
    ['BLOCK_ID', 'AUST_COLLATERALISED', 'UST_VALUE_COLLATERALISED'],
    axis=1,
)
collateral_fee_events_df['Source'] = 'Mirror'
collateral_fee_events_df['Destination'] = 'Void'
collateral_fee_events_df.columns = ['BLOCK_ID', 'AUST_AMOUNT', 'UST_AMOUNT', 'Source', 'Destination']
st.write('Collateral Withdraw Events: ', collateral_fee_events_df)


liquidation_events_df = aust_liquidated.filter(
    ['BLOCK_ID', 'AUST_COLLATERALISED', 'UST_VALUE_COLLATERALISED'],
    axis=1,
)
liquidation_events_df['Source'] = 'Mirror'
liquidation_events_df['Destination'] = 'Void'
liquidation_events_df.columns = ['BLOCK_ID', 'AUST_AMOUNT', 'UST_AMOUNT', 'Source', 'Destination']
st.write('Liquidation Events: ', liquidation_events_df)


liquidation_transfer_events_df = aust_transferred_back.filter(
    ['BLOCK_ID', 'AUST_TRANSFERRED_BACK', 'UST_VALUE_TRANSFERRED'],
    axis=1,
)
liquidation_transfer_events_df['Source'] = 'Mirror'
liquidation_transfer_events_df['Destination'] = 'Wallet'
liquidation_transfer_events_df.columns = ['BLOCK_ID', 'AUST_AMOUNT', 'UST_AMOUNT', 'Source', 'Destination']
st.write('Liquidation Transfer Backs: ', liquidation_transfer_events_df)


transfer_in_df = user_transfers_received_df.filter(
    ['BLOCK_ID', 'AUST_TRANSFERRED', 'UST_TRANSFERRED'],
    axis=1
)
transfer_in_df['Source'] = 'Void'
transfer_in_df['Destination'] = 'Wallet'
transfer_in_df.columns = ['BLOCK_ID', 'AUST_AMOUNT', 'UST_AMOUNT', 'Source', 'Destination']
st.write('Transfers In: ', transfer_in_df)

transfer_out_df = user_transfers_sent_df.filter(
    ['BLOCK_ID', 'AUST_TRANSFERRED', 'UST_TRANSFERRED'],
    axis=1
)
transfer_out_df['Source'] = 'Wallet'
transfer_out_df['Destination'] = 'Void'
transfer_out_df.columns = ['BLOCK_ID', 'AUST_AMOUNT', 'UST_AMOUNT', 'Source', 'Destination']
st.write('Transfers Out: ', transfer_out_df)


all_events_df = pd.concat(
    [
        deposit_events_df,
        redemption_events_df,
        collateral_deposit_events_df,
        collateral_withdraw_events_df,
        collateral_fee_events_df,
        liquidation_events_df,
        liquidation_transfer_events_df,
        transfer_in_df,
        transfer_out_df
    ]
)
all_events_df.set_index('BLOCK_ID')
st.write('All events: ', all_events_df)

