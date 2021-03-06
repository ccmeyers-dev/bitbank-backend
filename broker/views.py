from rest_framework.viewsets import ModelViewSet
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from django.db.models import Count

from authentication.models import Account

from .serializers import (
    PortfolioSerializer, TradeSerializer,
    DepositSerializer, WalletSerializer,
    TransactionSerializer, BillingSerializer,
    WithdrawalSerializer, AddWithdrawalSerializer,
    ExpertTraderSerializer, AddTradeSerializer
)
from .models import (
    Portfolio, Trade,
    Deposit, Wallet,
    Transaction,
    Withdrawal, Billing
)


class BillingViewSet(ModelViewSet):
    queryset = Billing.objects.all()
    serializer_class = BillingSerializer


class WithdrawalViewSet(ModelViewSet):
    queryset = Withdrawal.objects.all()
    serializer_class = WithdrawalSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get('id', None)
        user = self.request.user
        if user_id and user.is_admin:
            return self.queryset.filter(portfolio__id=user_id)
        return self.queryset.filter(portfolio=user.portfolio)


class TransactionViewSet(ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(portfolio=user.portfolio)


# undefined use atm
class PortfolioViewSet(ModelViewSet):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer


class TradeViewSet(ModelViewSet):
    queryset = Trade.objects.all()
    serializer_class = TradeSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get('id', None)
        user = self.request.user
        if user_id and user.is_admin:
            return self.queryset.filter(portfolio__id=user_id)
        return self.queryset


class DepositViewSet(ModelViewSet):
    queryset = Deposit.objects.all()
    serializer_class = DepositSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get('id', None)
        user = self.request.user
        if user_id and user.is_admin:
            return self.queryset.filter(portfolio__id=user_id)
        return self.queryset


class WalletViewSet(ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer


# special cases
class UserProfileView(APIView):
    def get(self, request):
        user = self.request.user
        serializer = PortfolioSerializer(user.portfolio)
        user_id = self.request.query_params.get('id', None)
        if user_id and user.is_admin:
            target_user = Portfolio.objects.get(id=user_id)
            serializer = PortfolioSerializer(target_user)
        return Response(serializer.data)


class SetExpertTraderView(APIView):
    def post(self, request, pk):
        user = self.request.user
        if user.is_admin:
            act = Portfolio.objects.get(id=pk)
            act.trade_score = request.data["score"]
            act.save()
            return Response({
                'status': 'operation successful'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'no permission'
            }, status=status.HTTP_401_UNAUTHORIZED)


class RemoveExpertTraderView(APIView):
    def post(self, request, pk):
        user = self.request.user
        if user.is_admin:
            act = Portfolio.objects.get(id=pk)
            act.trade_score = None
            act.save()
            return Response({
                'status': 'operation successful'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'no permission'
            }, status=status.HTTP_401_UNAUTHORIZED)


class ToggleAdminView(APIView):
    def post(self, request, pk):
        user = self.request.user
        if user.is_admin:
            act = Account.objects.get(id=pk)
            if act.is_admin:
                act.is_admin = False
            elif not act.is_admin:
                act.is_admin = True
            act.save()
            return Response({
                'status': 'operation successful'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'no permission'
            }, status=status.HTTP_401_UNAUTHORIZED)


class DeleteUserView(APIView):
    def post(self, request, pk):
        user = self.request.user
        if user.is_admin:
            act = Account.objects.get(id=pk)
            act.delete()
            return Response({
                'status': 'operation successful'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'no permission'
            }, status=status.HTTP_401_UNAUTHORIZED)


class AdminDashboardView(APIView):
    def get(self, request):
        name = self.request.user.first_name
        users = Portfolio.objects.count()
        trades = Trade.objects.filter(profit=0).count()
        withdrawals = Withdrawal.objects.annotate(
            bills=Count('billings')).filter(bills__lt=1).count()
        dummy_wallets = Wallet.objects.filter(
            address='Coming Soon').count() >= 1

        return Response({
            'name': name,
            'users': users,
            'trades': trades,
            'withdrawals': withdrawals,
            'dummy_wallets': dummy_wallets,
        }, status=status.HTTP_200_OK)


class ExpertTraderViewSet(ModelViewSet):
    queryset = Portfolio.objects.filter(trade_score__isnull=False)
    serializer_class = ExpertTraderSerializer


class AddTradeViewSet(ModelViewSet):
    queryset = Trade.objects.all()
    serializer_class = AddTradeSerializer


class AddWithdrawalViewSet(ModelViewSet):
    queryset = Withdrawal.objects.all()
    serializer_class = AddWithdrawalSerializer
