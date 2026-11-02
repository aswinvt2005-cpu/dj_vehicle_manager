from django.shortcuts import render
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class VehicleManager(APIView):

    def post(self, request):

        data = request.data

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO vehicle
                (vehicle_name, vehicle_number, vehicle_type, brand,
                rent_per_day, fuel_type, is_available)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, [
                data.get('vehicle_name'),
                data.get('vehicle_number'),
                data.get('vehicle_type'),
                data.get('brand'),
                data.get('rent_per_day'),
                data.get('fuel_type'),
                data.get('is_available', True)
            ])

        return Response(
            {'message': 'Vehicle added successfully'},
            status=status.HTTP_201_CREATED
        )

    def get(self, request):

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM vehicle")
            records = cursor.fetchall()

        data = []

        for row in records:
            data.append({
                'id': row[0],
                'vehicle_name': row[1],
                'vehicle_number': row[2],
                'vehicle_type': row[3],
                'brand': row[4],
                'rent_per_day': row[5],
                'fuel_type': row[6],
                'is_available': row[7]
            })

        return Response(data)


class VehicleDetails(APIView):

    def get(self, request, id):

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM vehicle WHERE id=%s", [id])
            row = cursor.fetchone()

        if row is None:
            return Response(
                {'message': 'Vehicle not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        data = {
            'id': row[0],
            'vehicle_name': row[1],
            'vehicle_number': row[2],
            'vehicle_type': row[3],
            'brand': row[4],
            'rent_per_day': row[5],
            'fuel_type': row[6],
            'is_available': row[7]
        }

        return Response(data)

    def put(self, request, id):

        data = request.data

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE vehicle SET
                vehicle_name=%s,
                vehicle_number=%s,
                vehicle_type=%s,
                brand=%s,
                rent_per_day=%s,
                fuel_type=%s,
                is_available=%s
                WHERE id=%s
            """, [
                data.get('vehicle_name'),
                data.get('vehicle_number'),
                data.get('vehicle_type'),
                data.get('brand'),
                data.get('rent_per_day'),
                data.get('fuel_type'),
                data.get('is_available'),
                id
            ])

            if cursor.rowcount == 0:
                cursor.execute("SELECT id FROM vehicle WHERE id=%s", [id])

                if cursor.fetchone() is None:
                    return Response(
                        {'message': 'Vehicle not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )

        return Response({'message': 'Vehicle updated successfully'})

    def delete(self, request, id):

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM vehicle WHERE id=%s", [id])

            if cursor.rowcount == 0:
                return Response(
                    {'message': 'Vehicle not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

        return Response({'message': 'Vehicle deleted successfully'})


class CustomerManager(APIView):

    def post(self, request):

        data = request.data

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO customer (name, email, phone, address)
                VALUES (%s, %s, %s, %s)
            """, [
                data.get('name'),
                data.get('email'),
                data.get('phone'),
                data.get('address')
            ])

        return Response(
            {'message': 'Customer added successfully'},
            status=status.HTTP_201_CREATED
        )

    def get(self, request):

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM customer")
            records = cursor.fetchall()

        data = []

        for row in records:
            data.append({
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'phone': row[3],
                'address': row[4]
            })

        return Response(data)


class RentalManager(APIView):

    def post(self, request):

        data = request.data

        vehicle_id = data.get('vehicle_id')
        customer_id = data.get('customer_id')
        rent_date = data.get('rent_date')
        return_date = data.get('return_date')

        with connection.cursor() as cursor:

            cursor.execute(
                "SELECT rent_per_day, is_available FROM vehicle WHERE id=%s",
                [vehicle_id]
            )

            vehicle = cursor.fetchone()

            if vehicle is None:
                return Response(
                    {'message': 'Vehicle not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            if not vehicle[1]:
                return Response(
                    {'message': 'Vehicle is not available'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            cursor.execute(
                "SELECT id FROM customer WHERE id=%s",
                [customer_id]
            )

            if cursor.fetchone() is None:
                return Response(
                    {'message': 'Customer not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            from datetime import date

            try:
                start_date = date.fromisoformat(rent_date)
                end_date = date.fromisoformat(return_date)

                total_days = (end_date - start_date).days

                if total_days <= 0:
                    return Response(
                        {'message': 'Return date must be after rent date'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            except (ValueError, TypeError):
                return Response(
                    {'message': 'Invalid rental dates'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            total_amount = total_days * vehicle[0]

            cursor.execute("""
                INSERT INTO rental
                (vehicle_id, customer_id, rent_date, return_date,
                total_days, total_amount, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, [
                vehicle_id,
                customer_id,
                rent_date,
                return_date,
                total_days,
                total_amount,
                'Booked'
            ])

            cursor.execute(
                "UPDATE vehicle SET is_available=FALSE WHERE id=%s",
                [vehicle_id]
            )

        return Response({
            'message': 'Vehicle rented successfully',
            'total_days': total_days,
            'total_amount': total_amount
        }, status=status.HTTP_201_CREATED)

    def get(self, request):

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT rental.id, vehicle.vehicle_name,
                customer.name, rental.rent_date,
                rental.return_date, rental.total_days,
                rental.total_amount, rental.status
                FROM rental
                JOIN vehicle ON rental.vehicle_id = vehicle.id
                JOIN customer ON rental.customer_id = customer.id
            """)

            records = cursor.fetchall()

        data = []

        for row in records:
            data.append({
                'id': row[0],
                'vehicle': row[1],
                'customer': row[2],
                'rent_date': row[3],
                'return_date': row[4],
                'total_days': row[5],
                'total_amount': row[6],
                'status': row[7]
            })

        return Response(data)


class ReturnVehicle(APIView):

    def put(self, request, id):

        with connection.cursor() as cursor:

            cursor.execute(
                "SELECT vehicle_id FROM rental WHERE id=%s AND status='Booked'",
                [id]
            )

            rental = cursor.fetchone()

            if rental is None:
                return Response(
                    {'message': 'Active rental not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            cursor.execute(
                "UPDATE rental SET status='Returned' WHERE id=%s",
                [id]
            )

            cursor.execute(
                "UPDATE vehicle SET is_available=TRUE WHERE id=%s",
                [rental[0]]
            )

        return Response({'message': 'Vehicle returned successfully'})
