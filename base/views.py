from django.http import Http404
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, filters
from base.pagination.PaginationClass import BlogContentPagination
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    BlogContentSerializer,
    BlogContentListSerializer,
    UserProfileSerializer,
    UserCommentSerializer,
    BlogPostLikeSerializer,
    FollowSerializer,
    SavedPostSerializer,
    QuestionSerializer,
    ChoiceSerializer,
    VotersSerializer,
)
from .models import (
    BlogContent,
    UserProfile,
    BlogPostLike,
    Follow,
    SavedPost,
    Question,
    Choice,
    Voters,
    Pro,
)
from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from django.db import connection
from django.db.models import Count, F, Prefetch
from datetime import timedelta, datetime
import stripe
import os
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_API_KEY")


class HealthCheck(APIView):
    def get(self, request):
        return Response("API Running!")


class UserRegistrationView(APIView):
    @swagger_auto_schema(
        request_body=UserRegistrationSerializer,
        responses={201: UserRegistrationSerializer},
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response("Registered successful", status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    serializer_class = UserLoginSerializer

    @swagger_auto_schema(
        request_body=UserLoginSerializer, responses={200: UserLoginSerializer}
    )
    def post(self, request):
        try:
            user = User.objects.get(username=request.data["username"])
            if not user.check_password(request.data["password"]):
                return Response("Invalid Password", status=status.HTTP_401_UNAUTHORIZED)
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "jwt": str(refresh.access_token),
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                }
            )
        except User.DoesNotExist:
            return Response("Invalid Username", status=status.HTTP_401_UNAUTHORIZED)


class BlogContentView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=BlogContentSerializer,
        responses={201: BlogContentSerializer, 400: "Bad Request", 401: "Unauthorized"},
    )
    def post(self, request):
        request.data._mutable = True
        tag_ids = request.data.get("tags")
        tag_ids_int = [int(i) for i in tag_ids.split(",")]
        request.data["tags"] = tag_ids_int
        serializer = BlogContentSerializer(data=request.data)
        if serializer.is_valid():
            # Assuming you have user authentication in place
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BlogContentListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(responses={200: BlogContentSerializer(many=True)})
    def get(self, request, pk=None):
        page_size = 8
        if pk is not None:
            try:
                blog_post = BlogContent.objects.get(pk=pk)
                serializer = BlogContentSerializer(blog_post)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except BlogContent.DoesNotExist:
                raise Http404
        else:
            blogs = BlogContent.objects.all()
            paginator = PageNumberPagination()
            paginator.page_size = page_size
            result_page = paginator.paginate_queryset(blogs, request)
            serializer = BlogContentListSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        request_body=BlogContentSerializer,
        responses={200: BlogContentSerializer, 400: "Bad Request", 403: "Forbidden"},
    )
    def put(self, request, pk):
        try:
            blog_post = BlogContent.objects.get(pk=pk)
        except BlogContent.DoesNotExist:
            return Response(
                {"detail": "Blog post not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if blog_post.author == request.user or request.user.is_staff:
            request.data._mutable = True
            tag_ids = request.data.get("tags")
            tag_ids_int = [int(i) for i in tag_ids.split(",")]
            request.data["tags"] = tag_ids_int
            serializer = BlogContentSerializer(
                blog_post, data=request.data, partial=True
            )

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"detail": "You do not have permission to update this blog post."},
                status=status.HTTP_403_FORBIDDEN,
            )

    @swagger_auto_schema(responses={204: "No Content", 403: "Forbidden"})
    def delete(self, request, pk):
        try:
            blog_post = BlogContent.objects.get(pk=pk)
        except BlogContent.DoesNotExist:
            raise Http404

        if blog_post.author == request.user or request.user.is_staff:
            blog_post.delete()
            return Response(
                {"detail": "Post Deleted!"}, status=status.HTTP_204_NO_CONTENT
            )
        else:
            return Response(
                {"detail": "You do not have permission to delete this blog post."},
                status=status.HTTP_403_FORBIDDEN,
            )


class UserProfileView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(responses={200: UserProfileSerializer})
    def get(self, request, username=None):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Please log in to view profiles"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if username is not None:
            try:
                user = User.objects.get(username=username)
                user_profile = UserProfile.objects.get(user=user)
                serializer = UserProfileSerializer(user_profile)
                return Response(serializer.data)
            except User.DoesNotExist:
                raise Http404
            except UserProfile.DoesNotExist:
                raise Http404
        else:
            # Return the profile of the authenticated user
            user_profile = UserProfile.objects.get(user=request.user)
            serializer = UserProfileSerializer(user_profile)
            return Response(serializer.data)

    # @swagger_auto_schema(
    #     request_body=UserProfileSerializer,
    #     responses={201: UserProfileSerializer}
    # )
    # def post(self, request):
    #     existing_user = UserProfile.objects.filter(user=request.user).first()
    #     if existing_user:
    #         return Response({'detail': 'User Profile Already Exists, Use Update to make'})
    #     serializer = UserProfileSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save(user=request.user)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     else:
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=UserProfileSerializer, responses={201: UserProfileSerializer}
    )
    def patch(self, request):
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)

        serializer = UserProfileSerializer(user_profile, data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCommentView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: UserCommentSerializer})
    def get(self, request, pk):
        try:
            blog_post = BlogContent.objects.get(id=pk)
        except BlogContent.DoesNotExist:
            return Response(
                {"error": "Blog post not found"}, status=status.HTTP_404_NOT_FOUND
            )
        comment = blog_post.usercomment_set.all()
        serializer = UserCommentSerializer(comment, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=UserCommentSerializer,
        responses={
            201: UserCommentSerializer,
            400: "Bad Request",
            401: "Unauthorized",
            404: "Blog post not found",
        },
    )
    def post(self, request, pk):
        try:
            blog_post = BlogContent.objects.get(pk=pk)
        except BlogContent.DoesNotExist:
            return Response(
                {"error": "Blog post not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, post=blog_post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BlogPostLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            blog_post = BlogContent.objects.get(pk=pk)
        except BlogContent.DoesNotExist:
            return Response(
                {"error": "Blog post not found"}, status=status.HTTP_404_NOT_FOUND
            )
        likes = blog_post.like.all()
        serializer = BlogPostLikeSerializer(
            likes, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @swagger_auto_schema(
        responses={
            200: "Post disliked successfully",
            201: "Post liked successfully",
            400: "Bad Request",
            401: "Unauthorized",
            404: "Blog post not found",
        }
    )
    def post(self, request, pk):
        try:
            blog_post = BlogContent.objects.get(pk=pk)
        except BlogContent.DoesNotExist:
            return Response(
                {"error": "Blog post not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Check if the user has already liked the post
        existing_like = BlogPostLike.objects.filter(
            user=request.user, post=blog_post
        ).first()

        if existing_like:
            # User has already liked the post, so dislike it
            existing_like.delete()
            return Response(
                {"message": "Post disliked successfully"}, status=status.HTTP_200_OK
            )
        else:
            # User has not liked the post, so like it
            like_data = {"user": request.user.id, "post": blog_post.id}
            serializer = BlogPostLikeSerializer(data=like_data)

            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"message": "Post liked successfully"},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DynamicSearchView(generics.ListAPIView):
    queryset = BlogContent.objects.all()
    serializer_class = BlogContentSerializer
    search_fields = ["content", "title"]
    filter_backends = (filters.SearchFilter,)
    pagination_class = BlogContentPagination

    @swagger_auto_schema(
        responses={200: BlogContentSerializer(many=True), 404: "Not Found"}
    )
    def get_queryset(self):
        search_param = self.request.query_params.get("search", None)
        if not search_param:
            return BlogContent.objects.none()
        queryset = BlogContent.objects.filter(
            content__icontains=search_param
        ) | BlogContent.objects.filter(title__icontains=search_param)
        return queryset

    def list(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if not queryset.exists():
            return Response(
                {"message": "Please provide some valid search input"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if page is not None:
            serializer = self.get_paginated_response(
                self.serializer_class(page, many=True).data
            )
            return Response(serializer.data)
        serializer = BlogContentSerializer(queryset, many=True)
        return Response(serializer.data)


class FilterRecentPostView(generics.ListAPIView):
    serializer_class = BlogContentSerializer
    pagination_class = BlogContentPagination

    def get_queryset(self):
        return BlogContent.objects.order_by("-created_at")


class PopularPostsView(APIView):
    def get(self, request):
        posts_with_counts = BlogContent.objects.annotate(
            like_count=Count("likes"),
        )
        popularity_score = F("like_count")
        ordered_posts = posts_with_counts.order_by(-popularity_score)
        serializer = BlogContentSerializer(ordered_posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TopAuthorsView(APIView):
    def get(self, request):
        authors_with_post_counts = UserProfile.objects.annotate(
            total_posts=Count("user__posts")
        )
        ordered_authors = authors_with_post_counts.order_by("-total_posts")[:5]
        serializer = UserProfileSerializer(ordered_authors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UsersPostView(APIView):
    def get(self, request, username):
        print(request)
        user = User.objects.get(username=username)
        users_posts = user.posts.all()
        serializer = BlogContentListSerializer(users_posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FollowView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = User.objects.get(username=request.user.username)
        following = user.following_set.all()
        followers = user.followers_set.all()
        serializer = FollowSerializer(
            following, many=True, context={"request": request}
        )
        serializer_2 = FollowSerializer(
            followers, many=True, context={"request": request}
        )
        return Response(
            {
                "following": [data["following_name"] for data in serializer.data],
                "followers": [data["follower_name"] for data in serializer_2.data],
            }
        )

    @swagger_auto_schema(
        responses={
            200: "Unfollowed successfully",
            201: "Followed successfully",
            400: "Bad Request",
            401: "Unauthorized",
            404: "User not found",
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"user_id": openapi.Schema(type=openapi.TYPE_INTEGER)},
        ),
    )
    def post(self, request):
        user_to_follow_id = request.data.get("user_id")
        user_to_follow = User.objects.get(id=user_to_follow_id)
        if request.user == user_to_follow:
            return Response(
                {"detail": "You cannot follow/unfollow yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            follow_instance = Follow.objects.get(
                follower=request.user, following=user_to_follow
            )
            follow_instance.delete()
            serializer = FollowSerializer(follow_instance)
            return Response(
                {"detail": f"You have unfollowed {user_to_follow.username}."},
                status=status.HTTP_200_OK,
            )

        except Follow.DoesNotExist:
            follow_instance = Follow.objects.create(
                follower=request.user, following=user_to_follow
            )
            serializer = FollowSerializer(follow_instance, context={"request": request})
            return Response(
                {
                    "detail": f"You are now following {user_to_follow.username}.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )


class FilterByTagsView(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "tags",
                openapi.IN_QUERY,
                description="Tag ID as a string",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: BlogContentSerializer(many=True)},
    )
    def get(self, request):
        try:
            tag_id = int(request.query_params.get("tags"))
            posts = BlogContent.objects.filter(tags=tag_id)
            paginator = PageNumberPagination()
            paginator.page_size = 8
            result_page = paginator.paginate_queryset(posts, request)
            serializer = BlogContentListSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)
        except (TypeError, ValueError):
            return Response({"error": "Invalid or missing tag ID"}, status=400)

        # serializer = BlogContentSerializer(posts, many=True)
        # return Response(serializer.data)


class SavedPostView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = User.objects.get(id=request.user.id)
        posts = user.saved_posts.all()
        serializer = SavedPostSerializer(posts, many=True, context={"request": request})
        return Response(serializer.data)

    @swagger_auto_schema(
        responses={
            200: "Post Unsaved",
            201: "Post Saved",
            400: "Bad Request",
            401: "Unauthorized",
            404: "Post Not Found",
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"post_id": openapi.Schema(type=openapi.TYPE_INTEGER)},
        ),
    )
    def post(self, request):
        try:
            post = BlogContent.objects.get(id=request.data.get("post_id"))
        except BlogContent.DoesNotExist:
            return Response(
                {"details": "Post not found"}, status=status.HTTP_404_NOT_FOUND
            )
        saved_post = SavedPost.objects.filter(user=request.user.id, post=post).first()
        if saved_post:
            saved_post.delete()
            return Response({"details": "Post Unsaved"}, status=status.HTTP_200_OK)
        else:
            saved_data = {"user": request.user.id, "post": post.id}
            serialzer = SavedPostSerializer(data=saved_data)
            if serialzer.is_valid():
                serialzer.save()
                return Response(
                    {"details": "Post Saved"}, status=status.HTTP_201_CREATED
                )


class VotersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response_data = []
        questions = Question.objects.prefetch_related("choices")
        for question in questions:
            question_data = QuestionSerializer(question).data
            response_data.append(question_data)
        return Response(response_data)

    @swagger_auto_schema(
        responses={
            200: "Vote Cast Successfully",
            400: "Bad Request - Please, select the right option or you have already voted for this choice.",
            401: "Unauthorized",
            404: "Choice or Question Not Found",
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "ques_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "choice_id": openapi.Schema(type=openapi.TYPE_INTEGER),
            },
        ),
    )
    def post(self, request):
        try:
            ques_id = request.data.get("ques_id")
            choice_id = request.data.get("choice_id")
            choices_for_question = Choice.objects.filter(question_id=ques_id)
            choice_list = []
            for choice in choices_for_question:
                choice_list.append(choice.id)
            if choice_id not in choice_list:
                return Response(
                    {"message": "Please, select right option"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            existing_vote = Voters.objects.filter(
                question=ques_id, voters=request.user, choice=choice_id
            ).first()
            if existing_vote:
                return Response(
                    {"message": "You have already voted for this choice."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            existing_vote_for_question = Voters.objects.filter(
                question=ques_id, voters=request.user
            ).first()
            if existing_vote_for_question:
                existing_vote_for_question.delete()

            serializer_data = {
                "question": ques_id,
                "voters": request.user.id,
                "choice": choice_id,
            }
            serializer = VotersSerializer(data=serializer_data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"message": "Vote cast successfully."}, status=status.HTTP_200_OK
                )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Choice.DoesNotExist:
            return Response(
                {"message": "Choice not found."}, status=status.HTTP_404_NOT_FOUND
            )


class PollsResultView(APIView):
    def post(self, request):
        ques_id = request.data.get("ques_id")
        if not ques_id:
            return Response(
                {"error": "ques_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            question = Question.objects.get(id=ques_id)
        except Question.DoesNotExist:
            return Response(
                {"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND
            )

        total_votes = Voters.objects.filter(question_id=ques_id).count()

        votes = (
            Voters.objects.filter(question_id=ques_id)
            .values("choice_id")
            .annotate(vote_count=Count("id"))
            .order_by("-vote_count")
        )

        # Convert votes to a dictionary for easier lookup
        votes_dict = {vote["choice_id"]: vote["vote_count"] for vote in votes}

        # Get all choices for the question
        choices = Choice.objects.filter(question_id=ques_id)

        votes_with_percentage = [
            {
                "choice_text": choice.choice_text,
                "vote_count": votes_dict.get(choice.id, 0),
                "percentage": (
                    (votes_dict.get(choice.id, 0) / total_votes * 100)
                    if total_votes > 0
                    else 0
                ),
            }
            for choice in choices
        ]

        response_data = {"total_votes": total_votes, "votes": votes_with_percentage}

        return Response(response_data, status=status.HTTP_200_OK)


class ProView(APIView):
    def get(self, request):
        user = request.user.id
        try:
            if Pro.objects.get(user=user):
                return Response(
                    {"details": "You Have Pro!!"}, status=status.HTTP_200_OK
                )

        except Pro.DoesNotExist:
            return Response(
                {"details": "You are a free memeber"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ProSubscriptionView(APIView):
    def post(self, request):
        req = request.data.get("subs")
        try:
            if Pro.objects.get(user=request.user.id):
                return Response("You Already Have Pro")
        except Pro.DoesNotExist:
            if req == "True":
                current_date = datetime.now().date()
                expiration_date = current_date + timedelta(days=30)
                Pro.objects.create(
                    user=request.user, is_pro=True, expiration_date=expiration_date
                )
                return Response("Congarts!! You are a Pro memeber now")


class CreateProductView(APIView):
    # permission_classes=[IsAdminUser]

    def post(self, request):
        name = request.data.get("name")
        price = int(request.data.get("price") * 100)
        currency = "inr"

        product = stripe.Product.create(
            name=name,
            default_price_data={
                "unit_amount": price,
                "currency": currency,
                "recurring": {"interval": "month", "interval_count": 1},
            },
        )
        return Response(product)


class AddCustomer(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        name = request.data.get("name")
        email = request.user.email
        customer = stripe.Customer.create(name=name, email=email)
        return Response(customer)


class CreatePaymentMethod(APIView):
    def post(self, request):
        payment = stripe.PaymentMethod.create(
            type="card",
            card={
                "number": "4242424242424242",
                "exp_month": 8,
                "exp_year": 2048,
                "cvc": "000",
            },
        )
        # stripe.PaymentMethod.attach(
        #     payment.id,
        #     customer="cus_PWWQHWxTGdiiGe",
        #     )
        return Response(payment)


class AttachCustomerWithPayment(APIView):
    def post(self, request):
        attach = stripe.PaymentMethod.attach(
            "pi_3OhrCvSCCapyiwy40H4Jg8Br",
            customer="cus_PWqEcX3PkjOIo6",
        )

        return Response(attach)


class CreateSubscription(APIView):
    def post(self, request):
        subscription = stripe.Subscription.create(
            customer="cus_PWqEcX3PkjOIo6",
            items=[{"price": "price_1OhUbcSCCapyiwy4RvgxoEoF"}],
            collection_method="send_invoice",
            days_until_due=1,
        )
        return Response(subscription)


class CreatePaymentIntent(APIView):
    def post(self, request):
        intent = stripe.SetupIntent.create(
            # amount=50000,
            # currency="inr",
            payment_method="pm_card_visa",
            customer="cus_PWqEcX3PkjOIo6",
        )
        return Response(intent)


class CreatePaymentLink(APIView):
    def post(self, request):
        payment_link = stripe.PaymentLink.create(
            line_items=[{"price": "price_1OhUbcSCCapyiwy4RvgxoEoF", "quantity": 1}],
        )
        return Response(payment_link)
